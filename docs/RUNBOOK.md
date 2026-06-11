# Runbook — driving the workflow (Steps 1–4)

Step-by-step companion to the [workflow in the README](../README.md#workflow). The CoFest goal is to drive these steps with an LLM and **capture the prompts and lessons learned** (with an optional Claude Skill as an extension). This runbook is the manual procedure — the spec your prompts should automate. Fill in commands and prompts as they mature.

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
Use the bundled synthetic study in [`../data/synthetic-study/`](../data/synthetic-study/): the dataset (`.xlsx` with a data-dictionary sheet, plus a `.csv` copy), the ~10-page protocol PDF, and an SOP PDF. (Or bring your own datasets + PDFs — the approach must work generically.)

## Step 1 — Fill the Canopy Study instance
Pull the live Canopy Study template from its well-known CEDAR location (`cedar-rest-mcp`). Infer field values from the protocol PDF + spreadsheet, resolve controlled terms with `bioportal-term-mcp`, and produce a valid `study-metadata.json` (`cedar-artifact-mcp`). **Keep this instance — it bootstraps the Canopy study in Step 4.**

## Step 2 — Create a domain-specific template
Design a flat, ontology-controlled template for the dataset (see [`../templates/domain-specific-template.yaml`](../templates/domain-specific-template.yaml) for the target shape). Author it with `cedar-artifact-mcp`, resolve controlled terms with `bioportal-term-mcp`, upload with `cedar-rest-mcp`, and verify with `cedar-cee-mcp` or the CEDAR UI.

## Step 3 — Fill the domain-specific instance
Pull the template authored in Step 2. Infer values from the artifacts, produce a valid `domain-specific-metadata.json`, and upload it to CEDAR.

## Step 4 — Create the study in Canopy
Create a new study in Canopy, bootstrapping it from the **Step 1** `study-metadata.json`, with files attached:
`study-metadata.json` (pre-fills study fields), `domain-specific-template.json` + `domain-specific-metadata.json` (added as a new category and rendered).
Staging: <https://staging.canopyplatform.org/> · Production (coming): <https://canopy.stanford.edu/>

## Definition of done
You can take the example study from raw files to a registered Canopy submission with an LLM doing the heavy lifting — both instances validate against their templates, controlled values resolve to real ontology term IDs — and you've **captured the prompts and a lessons-learned writeup** so someone else could repeat it on *different* inputs. (Extension: the same flow packaged as a one-step Claude Skill.)
