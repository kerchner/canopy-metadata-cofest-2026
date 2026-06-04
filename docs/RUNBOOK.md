# Runbook — running the pipeline (Steps 0–4)

Step-by-step companion to the [workflow in the README](../README.md#workflow). Fill in commands as the pipeline matures during CoFest.

## Prerequisites

- A CEDAR account + API key — <https://cedar.metadatacenter.org/>
- A BioPortal account + API key — <https://bioportal.bioontology.org/>
- The CEDAR MCP servers installed and registered with your LLM client:
  - [`cedar-artifact-mcp`](https://github.com/metadatacenter/cedar-artifact-mcp) (author/validate templates & instances)
  - [`bioportal-term-mcp`](https://github.com/metadatacenter/bioportal-term-mcp) (ontology lookups)
  - `cedar-rest-mcp` (push/pull to CEDAR) — *in development*
  - `cedar-cee-mcp` (view/render templates) — *in development*

```bash
export CEDAR_API_KEY=...        # do NOT commit
export BIOPORTAL_API_KEY=...
```

## Step 0 — Inputs
Use the bundled synthetic study in [`../data/synthetic-study/`](../data/synthetic-study/): a dataset spreadsheet, a protocol PDF, and an SOP PDF. (Or bring your own XLSX + PDFs.)

## Step 1 — Author a domain-specific template
Design a flat, ontology-controlled template for the dataset (see [`../templates/domain-specific-template.yaml`](../templates/domain-specific-template.yaml) for the target shape). Author it with `cedar-artifact-mcp`, resolve controlled terms with `bioportal-term-mcp`, upload with `cedar-rest-mcp`, and verify with `cedar-cee-mcp` or the CEDAR UI.

## Step 2 — Fill the Canopy Study instance
Pull the live Canopy Study template from its well-known CEDAR location (`cedar-rest-mcp`). Infer field values from the protocol PDF + spreadsheet and produce a valid `study-metadata.json` (`cedar-artifact-mcp`).

## Step 3 — Fill the domain-specific instance
Pull the template authored in Step 1. Infer values from the artifacts, produce a valid `domain-specific-metadata.json`, and upload it to CEDAR.

## Step 4 — Submit to Canopy
Register the study in Canopy with files attached:
`study-template.json`, `study-metadata.json`, `domain-specific-template.json`, `domain-specific-metadata.json`.
Staging: <https://staging.canopyplatform.org/> · Production (coming): <https://canopy.stanford.edu/>

## Definition of done
A reviewer can take the synthetic study from raw files to a registered Canopy submission, with both instances validating against their templates and controlled values resolving to real ontology term IDs.
