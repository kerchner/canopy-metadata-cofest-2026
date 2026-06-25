# /// script
# requires-python = ">=3.8"
# dependencies = ["psutil"]
# ///
"""stop_mcps.py - list (and optionally stop) the running CEDAR/BioPortal MCP servers.

Companion to download_mcps.py. The downloader installs jars and writes config; this script
manages the *running* server processes your LLM client (e.g. Claude Desktop) spawned from them.

Why it exists: clients launch each MCP server over stdio through a wrapper chain
(disclaimer -> shim -> java, or uvx -> python). On reconnect/reload they don't always reap the
old process, so duplicate generations pile up; and a SIGTERM to the wrapper doesn't always reach
the real process, leaving true orphans (reparented to init/launchd). Those orphans hold the uv
cache lock that can stall download_mcps.py, and they waste memory. This sweeps them cleanly.

  uv run scripts/stop_mcps.py            # list what's running (no killing)
  uv run scripts/stop_mcps.py stop       # stop them (prompts to confirm)
  uv run scripts/stop_mcps.py stop --yes # stop them, no prompt (for scripts/CI)
  uv run scripts/stop_mcps.py --dir ~/mcp ...   # match jars in a non-default folder

Scope is deliberately tight: it only matches the exact jar paths under --dir and the specific
bioportal-term-mcp uvx package, so it can never catch unrelated java or python processes.
Cross-platform: macOS / Linux / Windows.
"""
import argparse
import os
import sys
import time
from pathlib import Path

import psutil

# Same jars download_mcps.py installs; matched by their absolute path so nothing else is caught.
JAVA_MCPS = ["cedar-artifact-mcp", "cedar-artifact-rest-mcp", "cedar-cee-mcp"]
# The Python MCP runs via `uvx ... bioportal-term-mcp`; matched by this token in the command line.
UVX_MCP_TOKEN = "bioportal-term-mcp"


def info(m): print(m, file=sys.stderr)


def find_servers(jar_dir):
    """Return [(label, psutil.Process)] for every running MCP server we recognise."""
    jar_paths = {name: str(jar_dir / f"{name}.jar") for name in JAVA_MCPS}
    me = os.getpid()
    found = []
    for proc in psutil.process_iter(["pid", "cmdline"]):
        if proc.info["pid"] == me:
            continue  # never match ourselves
        try:
            cmdline = " ".join(proc.info["cmdline"] or [])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
        if not cmdline:
            continue
        label = None
        for name, path in jar_paths.items():
            if path in cmdline:
                label = name
                break
        if label is None and UVX_MCP_TOKEN in cmdline:
            label = UVX_MCP_TOKEN
        if label:
            found.append((label, proc))
    return found


def is_orphan(proc):
    """True if the process was reparented to init/launchd (POSIX only; always False on Windows)."""
    if os.name != "posix":
        return False
    try:
        return proc.ppid() == 1
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False


def _safe_ppid(proc):
    try:
        return proc.ppid()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return None


def print_table(servers, verbose=False):
    if not servers:
        info("No CEDAR/BioPortal MCP servers running.")
        return
    # A single healthy launch is several processes deep — the client execs a wrapper chain
    # (disclaimer -> shim -> java, or disclaimer -> uvx -> python), and every link matches our
    # filter. So the meaningful count is *chain roots*: a matched process whose parent is NOT itself
    # a matched process. One root = one healthy instance; >1 root = real duplication (un-reaped
    # reconnects). The wrapper-chain PIDs are noise for the common case, so they stay hidden unless
    # -v is passed or something's actually wrong.
    matched_pids = {p.pid for _, p in servers}
    by_label = {}
    for label, proc in servers:
        by_label.setdefault(label, []).append(proc)

    summary = {}  # label -> (roots, all_procs, has_orphan)
    for label in sorted(by_label):
        procs = by_label[label]
        roots = [p for p in procs if _safe_ppid(p) not in matched_pids]
        has_orphan = any(is_orphan(p) for p in procs)
        summary[label] = (roots, procs, has_orphan)

    dupes = [l for l, (r, _, _) in summary.items() if len(r) > 1]
    orphans = [l for l, (_, _, o) in summary.items() if o]
    healthy = not dupes and not orphans

    if healthy:
        info(f"\nMCP servers: {len(summary)} running, all healthy (one instance each).")
    else:
        bits = []
        if dupes:
            bits.append(f"{len(dupes)} with duplicate instances")
        if orphans:
            bits.append(f"{len(orphans)} with orphaned processes")
        info(f"\nMCP servers: {len(summary)} running, " + ", ".join(bits) + ".")
    info("-" * 48)

    for label, (roots, procs, has_orphan) in summary.items():
        if len(roots) > 1:
            mark, note = "DUP ", f"  {len(roots)} instances (expected 1) — roots: " \
                                 + ", ".join(str(p.pid) for p in roots)
        elif has_orphan:
            mark, note = "ORPH", "  orphaned process present (parent gone)"
        else:
            mark, note = " ok ", ""
        info(f"  [{mark}] {label}{note}")

    # Full per-process tree: on demand (-v), or automatically when there's something to investigate.
    if verbose or dupes or orphans:
        info("\nprocess detail:")
        for label, (roots, procs, _) in summary.items():
            children = {}
            for p in procs:
                children.setdefault(_safe_ppid(p), []).append(p)

            def emit(proc, depth):
                ppid = _safe_ppid(proc)
                tag = "  [ORPHAN: reparented to init/launchd]" if is_orphan(proc) else ""
                prefix = "    " + ("  " * depth) + ("- " if depth else "")
                info(f"{prefix}pid {proc.pid:<7} ppid {ppid if ppid is not None else '?':<7}{tag}")
                for child in children.get(proc.pid, []):
                    emit(child, depth + 1)

            info(f"  {label}:")
            for root in roots:
                emit(root, 0)
    elif not verbose:
        info("\n(run with -v to see process IDs / launch chains)")


def stop_servers(servers, timeout=5):
    """SIGTERM every match, wait, then SIGKILL whatever ignored it (the stubborn orphans)."""
    procs = [p for _, p in servers]
    for proc in procs:
        try:
            proc.terminate()  # SIGTERM on POSIX, TerminateProcess on Windows
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    gone, alive = psutil.wait_procs(procs, timeout=timeout)
    for proc in alive:
        try:
            proc.kill()  # SIGKILL / hard terminate for any survivor
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    psutil.wait_procs(alive, timeout=timeout)
    info(f"\nStopped {len(procs)} process(es)"
         + (f" ({len(alive)} needed a hard kill)." if alive else "."))


def main():
    ap = argparse.ArgumentParser(
        description="List or stop the running CEDAR/BioPortal MCP servers (companion to download_mcps.py).")
    ap.add_argument("action", nargs="?", default="list", choices=["list", "stop"],
                    help="'list' (default) just shows what's running; 'stop' terminates them.")
    ap.add_argument("--dir", help="folder the jars live in (default: ~/mcp) — matches download_mcps.py")
    ap.add_argument("--yes", "-y", action="store_true", help="stop without the confirmation prompt")
    ap.add_argument("--verbose", "-v", action="store_true",
                    help="show every PID and the full launch chain (hidden by default when healthy)")
    args = ap.parse_args()

    jar_dir = Path(args.dir or os.environ.get("MCP_DIR") or (Path.home() / "mcp")).expanduser()

    servers = find_servers(jar_dir)
    print_table(servers, verbose=args.verbose)

    if args.action == "list" or not servers:
        return

    # action == "stop": confirm unless --yes (or refuse silently in a non-interactive shell).
    if not args.yes:
        if not sys.stdin.isatty():
            info("\n  ! refusing to stop without confirmation in a non-interactive shell — "
                 "re-run with --yes.")
            sys.exit(1)
        ans = input(f"\nStop these {len(servers)} process(es)? [y/N] ").strip().lower()
        if ans not in ("y", "yes"):
            info("  - aborted; nothing stopped.")
            return

    stop_servers(servers)
    info("  - your client will re-spawn any server it still needs on next use/reconnect.")


if __name__ == "__main__":
    main()
