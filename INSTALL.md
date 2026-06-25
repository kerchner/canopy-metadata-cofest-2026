# Setup

## 1. Fork the repo and clone your fork

Fork it so you have your own copy to commit your work to, then clone that fork to your machine.

```bash
# Option A — GitHub CLI: forks and clones in one step
gh repo fork canopy-datahub/canopy-metadata-cofest-2026 --clone
cd canopy-metadata-cofest-2026
```

```bash
# Option B — plain git: click "Fork" on GitHub first, then clone YOUR fork
git clone https://github.com/YOUR_USERNAME/canopy-metadata-cofest-2026.git
cd canopy-metadata-cofest-2026
```

> **Do your work in [`work/`](work/).** Keep everything you produce — filled instances, your
> domain-specific template, prompts, the lessons-learned writeup — in that folder. Run every command
> below **from the repo root**.

## 2. Install the prerequisites

You need **Java 17+** (runs three of the servers) and **[uv](https://docs.astral.sh/uv/)** (runs the
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

On Windows, install [Temurin 17+](https://adoptium.net/) and [uv](https://docs.astral.sh/uv/).

Verify — each prints a version, and Java must be **17 or newer**:

```bash
java -version
uv --version
```

## 3. Get your two API keys

Two of the servers need a free API key. Grab both now — you'll pass them to the script in step 4 (or
it'll prompt you for them):

- **BioPortal** (used by `bioportal-term-mcp`) — sign in, or create a free account, at
  [bioportal.bioontology.org/account](https://bioportal.bioontology.org/account); your key is shown
  right on that page.
- **CEDAR** (used by `cedar-artifact-rest-mcp`) — sign in, or create a free account, at
  [cedar.metadatacenter.org](https://cedar.metadatacenter.org). Once logged in, click the person
  icon in the top-right corner to open your profile, where your API key is shown.

> **Never commit your keys.** `.gitignore` already excludes the usual files.

## 4. Download the servers and create the config

Run one command **from the repo root**. It downloads the four servers and prints a ready-to-paste
configuration block for your client, with the file paths and your keys already filled in:

```bash
uv run scripts/download_mcps.py --cedar-key YOUR_CEDAR_KEY --bioportal-key YOUR_BIOPORTAL_KEY
```

- Leave a key off and it'll simply ask you for it.
- Want the files somewhere other than `~/mcp`? Add `--dir /your/path`.
- Don't use `uv`? `python3 scripts/download_mcps.py` works the same way.

The configuration it produces is a small block of **JSON** — the standard way an LLM client is told
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

> **Claude Code shortcut.** Code can register a server straight from the shell, no file editing:
> `claude mcp add cedar-artifact --scope user -- "$(which java)" -jar "$HOME/mcp/cedar-artifact-mcp.jar"`
> (add `--env KEY=value` for the rest/bioportal keys). The pasted block works just as well.

## 6. Check it worked

In the client you just set up, ask the LLM (Claude, or whichever model you're using) to *"ping all
four MCP servers."* Each one should answer — that confirms the client started the servers and
connected to them. Now go to the [workflow](README.md#workflow).

## Updating to a new version

If we need to ship updates to the MCP servers during the hackathon, you can pick them up by
**running the same command again** from the repo root, then restarting your client:

```bash
uv run scripts/download_mcps.py
```

It pulls the newest version of each server and refreshes everything. Your configuration doesn't change, so
there's nothing to re-paste.

If you installed the jars somewhere other than `~/mcp` (using `--dir`), pass that **same `--dir`**
when updating — otherwise the new jars land in a different folder than the one your configuration
points at, and your client keeps running the old ones:

```bash
uv run scripts/download_mcps.py --dir /your/path
```

## Notes & troubleshooting

- **The browser server (`cedar-cee-mcp`)** opens forms on your own machine, so it needs a local
  browser and an internet connection — it won't work from a remote or headless environment.
- **`bioportal-term-mcp`'s first launch** downloads the package once (needs internet); after that
  it starts fast and works offline.
- **Quick check without a client** — pipe an initialize message to any Java server and you should
  get a single line of JSON back:
  `echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"t","version":"0"}}}' | java -jar <the-jar>`
- **See it in action** — each server's GitHub README has an example walkthrough. Together the flow
  is: author a template → add ontology terms → show/fill it as a form → save it.
- **Building from source** (only if you're tinkering): each repo's README covers it.
