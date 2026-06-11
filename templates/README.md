# Templates

Two CEDAR templates drive the workflow. The `.yaml` files here are **readable mirrors / specs** — the authoritative artifacts are CEDAR templates (JSON-LD) authored and validated with [`cedar-artifact-mcp`](https://github.com/metadatacenter/cedar-artifact-mcp).

| File | Role | Created/used in |
|---|---|---|
| `canopy-study-template.yaml` | The shared, study-level template every Canopy submission uses (RADx-derived). Pulled live from CEDAR, filled first. | Workflow Step 1 |
| `domain-specific-template.yaml` | A ~20-field flat, ontology-controlled template describing *this* study's dataset. Authored by the artifact. | Workflow Steps 2–3 |

Controlled fields name the ontology their values must come from (NCBITaxon, MONDO, NCIT, UBERON, EDAM, UO, …); resolve them to real term IDs with [`bioportal-term-mcp`](https://github.com/metadatacenter/bioportal-term-mcp).

The filled **instances** (`study-metadata.json`, `domain-specific-metadata.json`) are produced at runtime against the synthetic study in [`../data/synthetic-study/`](../data/synthetic-study/) and are themselves deliverables.
