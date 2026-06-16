# Templates

This folder holds the **one template we provide** — the Canopy Study template. The `.yaml` is a **readable mirror / spec**; the authoritative artifact is a CEDAR template (JSON-LD) you pull live from CEDAR and fill with [`cedar-artifact-mcp`](https://github.com/metadatacenter/cedar-artifact-mcp).

| File | Role | Used in |
|---|---|---|
| `canopy-study-template.yaml` | The shared, study-level template every Canopy submission uses (RADx-derived). Pulled live from CEDAR, filled first. | Workflow Step 1 |

The **domain-specific template is not here on purpose** — designing it (≈20 fields, ontology-controlled, mirroring the example dataset) is the Step 2 task, so there's no template to copy. Controlled fields should name the ontology their values come from (MONDO, NCIT, GAZ, …); resolve them to real term IDs with [`bioportal-term-mcp`](https://github.com/metadatacenter/bioportal-term-mcp).

The filled **instances** (`study-metadata.json`, `domain-specific-metadata.json`) are produced at runtime against the synthetic study in [`../data/synthetic-study/`](../data/synthetic-study/) and are themselves deliverables.
