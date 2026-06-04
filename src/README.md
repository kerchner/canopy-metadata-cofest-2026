# src

Pipeline code. At CoFest this fills out into the Step 1–4 workflow; right now it contains the data generator.

| File | Purpose |
|---|---|
| `gen_data.py` | Regenerates the synthetic study in `../data/synthetic-study/` (fixed seed → reproducible). Needs `openpyxl` and `reportlab`. |

Planned modules (good first issues):

- `parse/` — deterministic file & header parsing (XLSX, CSV, data dictionaries, PDF text).
- `extract/` — LLM-based structured extraction from artifacts.
- `jsonld/` — assemble CEDAR-valid JSON-LD instances.
- `validate/` — validate instances against templates via `cedar-artifact-mcp`.
- `submit/` — push study + files to Canopy (Step 4).
