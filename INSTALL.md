# MCP servers — install

> One-time setup. Gets the four CEDAR MCP servers running with your LLM client so you can drive the [workflow](README.md#workflow). For *what* the servers are and *why*, see the [main README](README.md#mcp-servers).

Four small MCP servers let your AI assistant work with metadata templates end to end —
authoring them, looking up ontology terms, filling them out as forms in your browser, and saving
them to a server. This guide gets all four running with your LLM client in three steps. Nothing to
build or compile — you download a script, run it, and paste what it gives you.

| Server | What it does | Stack |
|---|---|---|
| [cedar-artifact-mcp](https://github.com/metadatacenter/cedar-artifact-mcp) | Author & validate templates, elements, fields, and instances; convert YAML ↔ JSON | Java |
| [bioportal-term-mcp](https://github.com/metadatacenter/bioportal-term-mcp) | Look up ontologies, classes, and value sets in BioPortal (real IRIs, not guesses) | Python |
| [cedar-cee-mcp](https://github.com/metadatacenter/cedar-cee-mcp) | Render templates and instances as real forms in your browser, and collect what's filled in | Java |
| [cedar-artifact-rest-mcp](https://github.com/metadatacenter/cedar-artifact-rest-mcp) | Save, fetch, and validate artifacts on a live CEDAR server | Java |

Works with any MCP-capable client — tested with **Claude Desktop, Claude Code, Cursor, Windsurf,
and Cline**. (VS Code's built-in MCP support uses a different configuration format and isn't covered here.)

## What you'll need

- **An MCP-capable LLM client** (Claude, ChatGPT, Gemini, …) — you bring the license; we don't provide one.
- **Java 17 or newer** — runs the three Java servers.
- **[uv](https://docs.astral.sh/uv/)** — runs the Python server, and the install script below.
- **Two free API keys** — one each from BioPortal and CEDAR (that's step 1, next).

## 1. Get your API keys

Two of the servers need a free API key, so grab both before you install. You'll give them to the
script in step 2 (or it'll prompt you for them):

- **BioPortal** (used by `bioportal-term-mcp`) — sign in, or create a free account, at
  [bioportal.bioontology.org/account](https://bioportal.bioontology.org/account); your key is shown
  right on that page.
- **CEDAR** (used by `cedar-artifact-rest-mcp`) — sign in, or create a free account, at
  [cedar.metadatacenter.org](https://cedar.metadatacenter.org). Once logged in, click the person
  icon in the top-right corner to open your profile, where your API key is shown.

## 2. Download the servers and create an MCP configuration file

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
in step 3.

## 3. Paste the MCP configuration into your client

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

**Check it worked.** In the client you just set up, ask the LLM (Claude, or whichever model you're
using) to *"ping all four MCP servers."* Each one should answer — that confirms the client started
the servers and connected to them.

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
