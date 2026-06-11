# src

Where the **deliverable** lives: the curated **prompts and strategies** that drive the [Step 1–4 workflow](../README.md#workflow), and — as an extension — an optional reusable Claude Skill. Right now it holds the example-data generator.

| File | Purpose |
|---|---|
| `gen_data.py` | Regenerates the synthetic *example* study in `../data/synthetic-study/` (fixed seed → reproducible). Needs `openpyxl` and `reportlab`. |

Expected additions during the CoFest (see the README's [deliverable](../README.md#the-deliverable) section):

- **`prompts/`** — the prompts that drive Steps 1–4, with notes on order, context to supply, and guardrails.
- **Helper scripts** (optional) — pull text/tables/headers from XLSX, CSV, data dictionaries, and PDFs to feed the model.
- **An optional Claude Skill** — packaging the prompts + helpers so the workflow runs in one step. Orchestrates the CEDAR MCP servers: author/validate (`cedar-artifact-mcp`), term lookup (`bioportal-term-mcp`), repository push/pull (`cedar-rest-mcp`), view (`cedar-cee-mcp`), then bootstraps the Canopy study (Step 4).

The narrative writeup (prompts + lessons learned) lives in [`../docs/`](../docs/).
