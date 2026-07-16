# Setup

## 1. Fork the repo and clone your fork

Fork it so you have your own copy to commit your work to, then clone that fork to your machine.

**Option A** — GitHub CLI: forks and clones in one step

1. Ensure you have the GitHub CLI installed
2. Execute the instructions below in a terminal.
```bash
gh repo fork canopy-datahub/canopy-metadata-cofest-2026 --clone
cd canopy-metadata-cofest-2026
```

**Option B** — plain git: click "Fork" on GitHub first, then clone YOUR fork

1. Go to the GitHub Repo Page: [https://github.com/canopy-datahub/canopy-metadata-cofest-2026](https://github.com/canopy-datahub/canopy-metadata-cofest-2026)
2. Click "Fork" in the top right corner of the page and follow prompts
3. Execute the instructions below in a terminal (**_be sure to replace YOUR_USERNAME with your actual user name_**)
   
```bash
git clone https://github.com/YOUR_USERNAME/canopy-metadata-cofest-2026.git
cd canopy-metadata-cofest-2026
```

> **Do your work in `work/`.** Keep everything you produce — filled instances, your
> domain-specific template, prompts, the lessons-learned writeup — in that folder. Run every command
> below **from the repo root**.

## 2. Install the prerequisites

You need **Java 17+** (runs three of the servers) and **uv** (runs the
Python server and the install script).

```bash
# macOS (Homebrew)
brew install openjdk@17 uv
```

```bash
# Linux — uv via the official installer, Java from your package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
sudo apt-get install -y openjdk-17-jdk        # Debian/Ubuntu
```

On Windows, install [Temurin 17+](https://adoptium.net/) and uv.

Verify — each prints a version, and Java must be **17 or newer**:

```bash
java -version
uv --version
```

## 3. Get your two API keys

Two of the servers need a free API key. Grab both now — you'll pass them to the script in step 4 (or
it'll prompt you for them):

- **BioPortal** (used by `bioportal-term-mcp`) — sign in, or create an account, at
  [BioPortal](https://bioportal.bioontology.org/accounts/new). After logging in, your API key will be available on the Account Settings page, which you can access by clicking your username in the top-right menu.
- **CEDAR** (used by `cedar-artifact-rest-mcp`) — sign in, or create a free account, at
  [cedar.metadatacenter.org](https://cedar.metadatacenter.org). Once logged in, click the person
  icon in the top-right corner to open your profile, where your API key is shown. CEDAR may display
  it as `apiKey <RAWKEY>` — the key itself is **only the `<RAWKEY>` part**. The `apiKey ` prefix is
  just the `Authorization` header value (e.g. for `curl`), not part of the key, so don't include it.

> **Never commit your keys.** `.gitignore` already excludes the usual files.

## 4. Download the MCPs and create the config

Run one command **from the repo root**. It downloads the four servers and prints a ready-to-paste
configuration block for your client, with the file paths and your keys already filled in:

```bash
uv run scripts/download_mcps.py --cedar-key YOUR_CEDAR_KEY --bioportal-key YOUR_BIOPORTAL_KEY
```

- Leave a key off and it'll ask you for it.
- Want the files somewhere other than `~/mcp`? Add `--dir /your/path`.
- Don't use `uv`? `python3 scripts/download_mcps.py` works the same way.

The configuration it produces is a block of **JSON** — the standard way an LLM client is told
which MCP servers exist and how to launch each one. The script writes it to
`~/mcp/mcpServers.json` and also prints it to your screen; that's what you'll hand to your client
in step 5.

## 5. Paste the config into your client

Add the printed block to your client's configuration file, then **restart the client**. Most
MCP-capable clients use the same `mcpServers` JSON structure to declare their servers, so the block
is identical no matter which client you use — only *where* that configuration file lives differs:

| Client | Configuration file (macOS) |
|---|---|
| **Claude Desktop** | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| **Claude Code** | `~/.claude.json` — or skip the file and run `claude mcp add` (see below) |
| **Cursor** | `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (per project) |
| **Windsurf** | `~/.codeium/windsurf/mcp_config.json` |
| **Cline** | `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json` — or the extension's *Configure MCP Servers* button |

On Windows, Claude Desktop is at `%APPDATA%\Claude\claude_desktop_config.json` and Windsurf at
`%USERPROFILE%\.codeium\windsurf\mcp_config.json`.

> **Merge it — don't overwrite the file.** A configuration file usually holds other settings (and
> maybe other MCP servers), so never replace the whole thing. The block is JSON: add its
> `mcpServers` entry to the file — and if an `mcpServers` section is already there, just drop these
> four servers inside it.

## 6. Check that it worked

In the client you just set up, ask the LLM (Claude, or whichever model you're using) to *"ping all
four MCP servers."* Each one should answer with a `pong` and its build version — something like:

| MCP server          | Status   | Build                         |
|---------------------|----------|-------------------------------|
| cedar-artifact      | ✅ pong   | cedar-artifact-mcp 1.0.0      |
| cedar-artifact-rest | ✅ pong   | cedar-artifact-rest-mcp 1.0.0 |
| cedar-cee           | ✅ pong   | cedar-cee-mcp 1.0.0           |
| bioportal-term      | ✅ pong   | bioportal-term-mcp 1.0.0      |

If all four answer, the client started the servers and connected to them.

## Updating to a new version

If we ship updates to the MCP servers during the CoFest, picking them up is the **same command
again** — but the order matters, because your client keeps a running copy of each server in memory.
A running server holds onto the old jar, so you won't see the new version until the client
relaunches it. Do it in this order:

1. **Quit your LLM client first** (fully quit, not just close the window) so it releases the running
   servers.
2. **Update** from the repo root:

   ```bash
   uv run scripts/download_mcps.py
   ```

   It pulls the newest version of each server and refreshes everything. Your configuration doesn't
   change, so there's nothing to re-paste. (If you installed the jars somewhere other than `~/mcp`
   with `--dir`, pass that **same `--dir`** here: `uv run scripts/download_mcps.py --dir /your/path`.)
3. **Restart your client**, then **ping all four again** and
   confirm the **Build** versions went up.

### If something looks off

If a server misbehaves or seems stuck on an old version, there's a companion script that finds and
kills the running servers:

```bash
uv run scripts/stop_mcps.py            # list what's running
uv run scripts/stop_mcps.py stop       # stop them (prompts to confirm)
```

**Stop your LLM client before running it.** While the client is up it will just respawn any server
you kill — so quit the client first, run `stop_mcps.py stop`, then re-run `download_mcps.py` and
restart the client.

## Notes & troubleshooting

- **The browser server (`cedar-cee-mcp`)** opens forms on your own machine, so it needs a local
  browser and an internet connection — it won't work from a remote or headless environment.
- **`bioportal-term-mcp`'s first launch** downloads the package once (needs internet); after that
  it starts fast and works offline.
