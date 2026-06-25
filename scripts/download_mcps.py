#!/usr/bin/env python3
"""download_mcps.py - install (or update) the MCP servers AND write your client configuration, in one run.

What it does, every run:
  1. downloads the latest jar of each Java MCP server into a folder (default: ~/mcp),
  2. prints a ready-to-paste "mcpServers" config block and saves it next to the jars,
  3. refreshes the Python MCP (bioportal-term-mcp), which runs from its @release branch via uvx.

Re-run it any time to update — it re-fetches the latest jars and rewrites the configuration.
Cross-platform: macOS / Linux / Windows.

Settings are plain command-line options — no environment variables needed. Anything you leave out
is asked for (or reused from a previous run):

  uv run scripts/download_mcps.py
  uv run scripts/download_mcps.py --dir ~/mcp --cedar-key APIKEYHERE --bioportal-key APIKEYHERE
  python3 scripts/download_mcps.py        # if you already have Python 3

Get the keys:  CEDAR  -> cedar.metadatacenter.org (your profile)
               BioPortal -> bioportal.bioontology.org/account
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

JAVA_MCPS = ["cedar-artifact-mcp", "cedar-artifact-rest-mcp", "cedar-cee-mcp"]


def info(m): print(m, file=sys.stderr)


def _human(n):
    return f"{n / 1024 / 1024:.1f} MB" if n and n > 0 else "?"


def download_jars(jar_dir):
    info(f"\nFetching latest MCP jars into {jar_dir}")
    info("--------------------------------")
    for r in JAVA_MCPS:
        url = f"https://github.com/metadatacenter/{r}/releases/latest/download/{r}.jar"
        dest, tmp = jar_dir / f"{r}.jar", jar_dir / f"{r}.jar.part"
        try:
            # 30s socket timeout so a stalled connection fails fast instead of hanging silently.
            with urllib.request.urlopen(url, timeout=30) as resp:  # follows redirects
                total = int(resp.headers.get("Content-Length") or 0)
                # Skip the transfer when the local jar already matches the remote size — turns a
                # re-run into a near-instant no-op instead of re-pulling ~40 MB unconditionally.
                if total and dest.exists() and dest.stat().st_size == total:
                    info(f"  - {r}.jar ({_human(total)}) up to date, skipping")
                    continue
                info(f"  - {r}.jar ({_human(total)})")
                got = 0
                with open(tmp, "wb") as f:
                    while True:
                        chunk = resp.read(1 << 16)
                        if not chunk:
                            break
                        f.write(chunk)
                        got += len(chunk)
                        if total:  # live progress, overwriting one line via carriage return
                            sys.stderr.write(
                                f"\r    {got * 100 // total:3d}%  {_human(got)} / {_human(total)}")
                            sys.stderr.flush()
                if total:
                    sys.stderr.write("\n")  # finish the progress line
            tmp.replace(dest)  # atomic swap; an existing jar stays put if the download fails
        except Exception as e:
            if tmp.exists():
                tmp.unlink()
            info(f"  x failed: {r}: {e}")
            sys.exit(1)
    # bioportal-term-mcp runs from the @release git branch via uvx, which caches the resolved
    # commit; clear its cache so the next launch re-fetches the latest (a no-op on a fresh install).
    # Best-effort: nudges uvx to re-pull the latest @release commit on next launch. It needs an
    # exclusive cache lock, which a *running* bioportal-term-mcp server (e.g. one your LLM client
    # already launched) holds — so a missing timeout here deadlocks the whole script. Cap it and
    # move on: a skipped clean just means uvx reuses its cached commit, which is harmless.
    uv = shutil.which("uv")
    if uv:
        try:
            subprocess.run([uv, "cache", "clean", "bioportal-term-mcp"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
        except subprocess.TimeoutExpired:
            info("  ! skipped uv cache clean (cache busy — a bioportal-term-mcp server is likely "
                 "running). Harmless; uvx will reuse its cached commit.")
        except Exception:
            pass


def reuse_keys(config_path):
    """Pull previously-entered keys from an existing configuration so re-runs don't re-ask."""
    try:
        servers = json.loads(config_path.read_text()).get("mcpServers", {})
        return (servers.get("cedar-artifact-rest", {}).get("env", {}).get("CEDAR_API_KEY"),
                servers.get("bioportal-term", {}).get("env", {}).get("BIOPORTAL_API_KEY"))
    except Exception:
        return None, None


def main():
    ap = argparse.ArgumentParser(
        description="Download the MCP server jars and write your LLM-client configuration, in one step.")
    ap.add_argument("--dir", help="folder to keep the jars in (default: ~/mcp)")
    ap.add_argument("--cedar-key", help="CEDAR API key (from cedar.metadatacenter.org profile)")
    ap.add_argument("--bioportal-key", help="BioPortal API key (from bioportal.bioontology.org/account)")
    args = ap.parse_args()

    jar_dir = Path(args.dir or os.environ.get("MCP_DIR") or (Path.home() / "mcp")).expanduser()
    jar_dir.mkdir(parents=True, exist_ok=True)

    download_jars(jar_dir)

    java, uvx = shutil.which("java"), shutil.which("uvx")
    if not java:
        info("\n  ! java not found on PATH — install Java 17+ and re-run.")
        sys.exit(1)
    if not uvx:
        info("\n  ! uvx not found on PATH — install uv (https://docs.astral.sh/uv/) and re-run.")
        sys.exit(1)

    # Keys: command-line option > environment > a previous configuration > interactive prompt.
    config_path = jar_dir / "mcpServers.json"
    prev_cedar, prev_bio = reuse_keys(config_path)
    cedar_key = args.cedar_key or os.environ.get("CEDAR_API_KEY") or prev_cedar
    bio_key = args.bioportal_key or os.environ.get("BIOPORTAL_API_KEY") or prev_bio
    if sys.stdin.isatty():
        if not cedar_key:
            cedar_key = input("\nCEDAR API key (cedar.metadatacenter.org -> profile): ").strip()
        if not bio_key:
            bio_key = input("BioPortal API key (bioportal.bioontology.org/account): ").strip()
    if not (cedar_key and bio_key):
        info("\n  ! jars are downloaded, but no API key(s) given — pass --cedar-key / --bioportal-key "
             "(or run interactively) to (re)write the configuration.")
        sys.exit(0)

    if not cedar_key.startswith("apiKey "):  # CEDAR expects the header value prefixed
        cedar_key = "apiKey " + cedar_key

    config = {
        "mcpServers": {
            "cedar-artifact": {"command": java,
                               "args": ["-jar", str(jar_dir / "cedar-artifact-mcp.jar")]},
            "bioportal-term": {"command": uvx,
                               "args": ["--from",
                                        "git+https://github.com/metadatacenter/bioportal-term-mcp@release",
                                        "bioportal-term-mcp"],
                               "env": {"BIOPORTAL_API_KEY": bio_key}},
            "cedar-cee": {"command": java,
                          "args": ["-jar", str(jar_dir / "cedar-cee-mcp.jar")]},
            "cedar-artifact-rest": {"command": java,
                                    "args": ["-jar", str(jar_dir / "cedar-artifact-rest-mcp.jar")],
                                    "env": {"CEDAR_API_KEY": cedar_key,
                                            "CEDAR_BASE_URL": "https://resource.metadatacenter.org"}},
        }
    }

    block = json.dumps(config, indent=2)
    config_path.write_text(block + "\n")
    print(block)  # stdout: clean and pipeable

    info(f"\n--------------------------------")
    info(f"  - jars in {jar_dir}; configuration saved to {config_path}")
    info("  - add the block above to your client's configuration file (see the instructions' client "
         "table), then restart the client.")
    info('  - already have an "mcpServers" block? merge these four entries into it.')


if __name__ == "__main__":
    main()
