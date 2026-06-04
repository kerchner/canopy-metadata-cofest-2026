# Canopy: AI-Assisted Metadata Generation

### ISMB/ECCB 2026 — BOSC CollaborationFest project

Help researchers register FAIR-aligned studies in minutes instead of hours by using LLMs and a set of CEDAR Model Context Protocol (MCP) servers to turn ordinary research artifacts — spreadsheets, data dictionaries, protocols, and papers — into draft, standards-compliant metadata for human review.

---

## Background

[Canopy](https://github.com/canopy-datahub) is an open-source platform for building FAIR-aligned scientific data hubs, derived from the [NIH RADx Data Hub](https://radxdatahub.nih.gov/) and powered by [CEDAR](https://cedar.metadatacenter.org/) metadata templates.

A common barrier for data contributors is the effort required to complete structured metadata forms by hand before a study or data file can be registered. Filling these forms is slow, error-prone, and intimidating — the "blank page" problem — and it is one of the biggest reasons otherwise valuable datasets never get described well enough to be found and reused.

In this CoFest project we will prototype an **AI-assisted workflow** that reads common research artifacts (CSV/Excel files, data dictionaries, supplementary PDFs, protocols, grants, papers) and generates **draft CEDAR-compatible metadata for human review**. The goal is not to replace expert curation, but to reduce blank-page friction, suggest likely values, anchor those values to real ontology terms, and make metadata submission faster and more consistent.

A natural foundation for this work is the set of **CEDAR MCP servers** we maintain — focused tool servers that let an LLM use CEDAR directly, without each AI integration having to reinvent the wiring (see [MCP Servers](#mcp-servers-the-foundation) below).

## Goals

### Core goals (the 2-day focus)

1. **Build an end-to-end AI pipeline** that, given a study's artifacts (a spreadsheet + a protocol/paper PDF), produces:
   - a filled **Canopy Study** metadata instance (against the shared Study template), and
   - a **domain-specific** template *plus* a filled instance for that study's data.
2. **Exercise the CEDAR MCP servers** end-to-end: author/validate templates and instances (`cedar-artifact-mcp`), look up controlled terms (`bioportal-term-mcp`), and push/pull artifacts to live CEDAR (`cedar-rest-mcp`).
3. **Produce shareable synthetic sample data** (a synthetic study) so anyone can run the pipeline without sensitive real data — included in this repo under [`data/`](data/).
4. **Define and document the deliverables clearly**: the pipeline is the final product, but the intermediate artifacts (templates and instances) are first-class deliverables too.

### Stretch goals

- Ingest a Canopy Study + attached files directly into Canopy as a new submission (study-template / study-metadata / domain-specific-template / domain-specific-metadata) — see [Workflow Step 4](#step-4--submit-to-canopy).
- A lightweight **review interface** so a curator can accept/edit suggested values before submission.
- Add a "Pre-fill from metadata JSON" button to the Canopy *Create Study* page.
- Confidence scores / provenance on each inferred field, so reviewers know what to check first.
- Evaluate against a held-out study to measure how much manual effort the pipeline actually saves.

## MCP Servers (the foundation)

The pipeline is built on focused [Model Context Protocol](https://modelcontextprotocol.io/) servers for CEDAR. They let any LLM client use CEDAR as a set of tools.

| MCP server | Status | What it does |
|---|---|---|
| [`cedar-artifact-mcp`](https://github.com/metadatacenter/cedar-artifact-mcp) | Production | Author and validate CEDAR templates and metadata instances. |
| [`bioportal-term-mcp`](https://github.com/metadatacenter/bioportal-term-mcp) | Production | Look up ontology terms in BioPortal so values are anchored to real, standard identifiers instead of guessed free text. |
| `cedar-rest-mcp` | In development | Interact with the CEDAR repository itself — save generated metadata, fetch existing templates, search what's already published. |
| `cedar-cee-mcp` | In development | View/render a template (alternative to the CEDAR UI). |

> **API keys:** Working against live CEDAR and BioPortal requires free accounts and API keys. See [Getting Started](#getting-started). Never commit keys — `.gitignore` already excludes the usual files.

## Workflow

The target pipeline, expressed as the journey of a researcher who arrives with their data and leaves with a registered, FAIR study.

### Step 0 — The researcher arrives
The user brings the artifacts from a study:
- **Datasets** — XLSX, relational exports, CSVs, etc.
- **Documents** — papers, protocol, grant, SOP, supplementary PDFs.

### Step 1 — Define a domain-specific CEDAR template
Design a template that describes the metadata for *this* study's datasets — controlled terms, field types, cardinality.
- Author it with **`cedar-artifact-mcp`**.
- Upload it to CEDAR with **`cedar-rest-mcp`** (requires a CEDAR account + API key).
- View/verify it with **`cedar-cee-mcp`** or the CEDAR UI.

### Step 2 — Infer the Canopy *Study* metadata
Automatically infer metadata for the shared **Canopy Study** template from the user's PDFs and datasets.
- We provide the Canopy Study template (a CEDAR template; YAML mirror included in [`templates/`](templates/)).
- **`cedar-rest-mcp`** pulls the live template from a well-known CEDAR location.
- **`cedar-artifact-mcp`** fills in a valid instance from the artifacts.

### Step 3 — Infer the domain-specific metadata
Automatically infer metadata for the **domain-specific template** created in Step 1.
- Pull down the user's own template from CEDAR.
- Use **`cedar-artifact-mcp`** to create a proper instance, inferring values from the PDFs/datasets.
- Upload the instance to CEDAR.

### Step 4 — Submit to Canopy
Register everything in Canopy as a new study, with files attached.
- `study-template.json` — used by Canopy in place of the current RADx template.
- `study-metadata.json` — *Create Study* page gets a button to upload this JSON and pre-fill the study fields.
- `domain-specific-template.json` + `domain-specific-metadata.json` — recognized, added as a new category, and rendered with the submission.

```
artifacts (xlsx + pdf)
        │
        ▼
[Step 1] design domain template ──► CEDAR
        │
        ▼
[Step 2] fill Study instance  ◄── pull Study template from CEDAR
        │
        ▼
[Step 3] fill domain instance ◄── pull domain template from CEDAR
        │
        ▼
[Step 4] submit study + files ──► Canopy
```

## Deliverables

The **pipeline** is the final deliverable. The **intermediate artifacts** are first-class deliverables in their own right:

- A runnable AI pipeline (Claude / Codex-driven) wiring the CEDAR MCP servers together across Steps 1–4.
- A **domain-specific CEDAR template** (≈20-field flat template, ontology-controlled) — see [`templates/`](templates/).
- A filled **Canopy Study instance** and a filled **domain-specific instance** (JSON-LD).
- **Synthetic sample data** so the pipeline is reproducible without real/sensitive data — see [`data/`](data/).
- Documentation: this README + step-by-step run notes in [`docs/`](docs/).

## What we provide (synthetic sample data)

So contributors can run the pipeline immediately, this repo ships a small **synthetic study** under [`data/synthetic-study/`](data/synthetic-study/):

- A **dataset spreadsheet** (`.xlsx`) of subject-level measurements.
- A **data dictionary** describing each column.
- A **protocol / methods PDF**.
- A **standard operating procedure (SOP)**.

These are AI-generated and entirely fictional — no real subjects or results.

## Repository structure

```
canopy-metadata-cofest-2026/
├── README.md                  ← this proposal
├── LICENSE                    ← GPL-3.0
├── .gitignore
├── data/
│   └── synthetic-study/       ← AI-generated sample study (spreadsheet, dictionary, protocol, SOP)
├── templates/                 ← Canopy Study template + domain-specific template (CEDAR + YAML mirrors)
├── src/                       ← pipeline code (parsing, LLM extraction, JSON-LD generation, validation)
├── docs/                      ← step-by-step run notes, contributor guide
└── images/                    ← diagrams / screenshots
```

## Getting Started

> Detailed, step-by-step instructions live in [`docs/`](docs/). High-level setup:

1. **Accounts & keys** — create free accounts and generate API keys:
   - CEDAR: <https://cedar.metadatacenter.org/>
   - BioPortal (for `bioportal-term-mcp`): <https://bioportal.bioontology.org/>
   Export them as environment variables (e.g. `CEDAR_API_KEY`, `BIOPORTAL_API_KEY`). **Do not commit keys.**
2. **Install the MCP servers** — [`cedar-artifact-mcp`](https://github.com/metadatacenter/cedar-artifact-mcp) and [`bioportal-term-mcp`](https://github.com/metadatacenter/bioportal-term-mcp) (plus `cedar-rest-mcp` / `cedar-cee-mcp` as they become available), and register them with your LLM client (Claude, ChatGPT/Codex, etc.).
3. **Grab the sample data** — everything you need is in [`data/synthetic-study/`](data/synthetic-study/).
4. **Run the workflow** — follow [Steps 0–4](#workflow).

## Who should join

Developers and researchers interested in open biomedical data, metadata standards, FAIR data hubs, schema-driven software, ontologies, and practical uses of AI in open science. Comfort with Python, JSON/JSON-LD, or LLM tooling helps, but there's room at every level — parsing, extraction, validation, ontology mapping, and UI all need hands.

## Team

| Name | Role | Affiliation |
|---|---|---|
| Atti (Egyedi) | Project lead / main contact | Stanford University |
| Martin | Workflow & pipeline design | Stanford University |
| Marcos | Canopy / project concept | Stanford University |

*Contributors welcome — open an issue or say hello at the CoFest.*

## Links

- **Canopy (code):** <https://github.com/canopy-datahub>
- **Canopy (staging):** <https://staging.canopyplatform.org/>
- **Canopy (production, coming):** <https://canopy.stanford.edu/>
- **NIH RADx Data Hub (paper):** <https://publichealth.jmir.org/2025/1/e72677/>
- **NIH RADx Data Hub (website):** <https://radxdatahub.nih.gov/>
- **CEDAR Workbench:** <https://cedar.metadatacenter.org/>
- **CEDAR Artifact MCP:** <https://github.com/metadatacenter/cedar-artifact-mcp>
- **BioPortal Term MCP:** <https://github.com/metadatacenter/bioportal-term-mcp>

## License

[GPL-3.0](LICENSE).
