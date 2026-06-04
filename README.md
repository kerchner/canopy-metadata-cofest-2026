# Canopy: AI-Assisted Metadata Generation

### CollaborationFest 2026 project [CoFest 2026](https://www.open-bio.org/events/bosc-2026/collaborationfest/)

Build a **reusable AI artifact** (a Claude Skill or Project) that turns any researcher's ordinary artifacts — spreadsheets, data dictionaries, protocols, papers — into draft, standards-compliant CEDAR metadata and a bootstrapped Canopy study, using a set of CEDAR Model Context Protocol (MCP) servers. The aim: register FAIR-aligned studies in minutes instead of hours, with a human still in the loop for review.

---

## Background

[Canopy](https://github.com/canopy-datahub) is an open-source platform for building FAIR-aligned scientific data hubs, derived from the [NIH RADx Data Hub](https://radxdatahub.nih.gov/) and powered by [CEDAR](https://cedar.metadatacenter.org/) metadata templates.

A common barrier for data contributors is the effort required to complete structured metadata forms by hand before a study or data file can be registered. Filling these forms is slow, error-prone, and intimidating — the "blank page" problem — and it is one of the biggest reasons otherwise valuable datasets never get described well enough to be found and reused.

In this CoFest project we will prototype an **AI-assisted workflow** that reads common research artifacts (CSV/Excel files, data dictionaries, supplementary PDFs, protocols, grants, papers) and generates **draft CEDAR-compatible metadata for human review**. The goal is not to replace expert curation, but to reduce blank-page friction, suggest likely values, anchor those values to real ontology terms, and make metadata submission faster and more consistent.

A natural foundation for this work is the set of **CEDAR MCP servers** we maintain — focused tool servers that let an LLM use CEDAR directly, without each AI integration having to reinvent the wiring (see [MCP Servers](#mcp-servers-the-foundation) below).

## Goals

**The deliverable is a reusable AI artifact** — most likely a **Claude Skill** or a **Claude Project** (an MCP server is probably *not* the right shape, since the MCP servers already exist) — that can **drive the full 4-step workflow on its own**. The synthetic study in this repo is only an example input; the artifact must generalize to *any* researcher's datasets and documents.

### Core goals (the 2-day focus)

1. **Decide the form of the deliverable** — a Claude Skill, a Claude Project, or another packaging that lets an LLM run the workflow end-to-end. (See [Deliverable](#the-deliverable) for the trade-offs.)
2. **Build that artifact** so it can drive [Steps 1–4](#workflow): fill the Canopy Study template, design a domain-specific template, fill it, and create the study in Canopy.
3. **Make it generic.** Given arbitrary input artifacts (spreadsheets, data dictionaries, protocols, papers, SOPs), it should produce valid CEDAR metadata — not just for our example study.
4. **Prove it on the example.** Run the artifact against the bundled [synthetic study](#what-we-provide-example-input-data) and show the four steps complete end-to-end.

### Stretch goals

- A lightweight **review interface** so a curator can accept/edit suggested values before submission.
- Add a "Pre-fill from metadata JSON" button to the Canopy *Create Study* page (supports [Step 4](#step-4--create-the-study-in-canopy)).
- Confidence scores / provenance on each inferred field, so reviewers know what to check first.
- Evaluate against a held-out study to measure how much manual effort the artifact actually saves.
- Package the artifact so others can install and run it against their own data in one step.

## MCP Servers (the foundation)

The deliverable is built **on top of** focused [Model Context Protocol](https://modelcontextprotocol.io/) servers for CEDAR — it orchestrates them, it doesn't replace them. They let any LLM client use CEDAR as a set of tools.

| MCP server | Status | What it does |
|---|---|---|
| [`cedar-artifact-mcp`](https://github.com/metadatacenter/cedar-artifact-mcp) | Production | Author and validate CEDAR templates and metadata instances. |
| [`bioportal-term-mcp`](https://github.com/metadatacenter/bioportal-term-mcp) | Production | Look up ontology terms in BioPortal so values are anchored to real, standard identifiers instead of guessed free text. |
| `cedar-rest-mcp` | In development | Interact with the CEDAR repository itself — save generated metadata, fetch existing templates, search what's already published. |
| `cedar-cee-mcp` | In development | View/render a template (alternative to the CEDAR UI). |

> **API keys:** Working against live CEDAR and BioPortal requires free accounts and API keys. See [Getting Started](#getting-started). Never commit keys — `.gitignore` already excludes the usual files.

## Workflow

This is the workflow the deliverable must drive. **Input (Step 0):** the researcher's artifacts — datasets (XLSX, relational exports, CSVs) and documents (papers, protocol, grant, SOP, supplementary PDFs). The bundled synthetic study is one such example; the workflow must work for any.

### Step 1 — Fill out the existing Canopy *Study* template
Using AI tools, infer values for the shared **Canopy Study** template from the artifacts and produce a valid instance.
- The Canopy Study template is an existing CEDAR template (readable mirror in [`templates/`](templates/)); pull it live from its well-known CEDAR location with **`cedar-rest-mcp`**.
- Fill in a valid instance from the PDFs/datasets with **`cedar-artifact-mcp`**, anchoring controlled values via **`bioportal-term-mcp`**.
- This Step 1 instance is what bootstraps the Canopy study in Step 4.

### Step 2 — Create a domain-specific template
Using AI tools, design a template that describes the metadata for *this* study's datasets — controlled terms, field types, cardinality (target shape in [`templates/domain-specific-template.yaml`](templates/domain-specific-template.yaml)).
- Author it with **`cedar-artifact-mcp`**; resolve controlled terms with **`bioportal-term-mcp`**.
- Upload it to CEDAR with **`cedar-rest-mcp`**; view/verify with **`cedar-cee-mcp`** or the CEDAR UI.

### Step 3 — Fill the domain-specific template
Create a valid instance of the Step 2 template.
- Pull the template back from CEDAR.
- Infer values from the artifacts and build the instance with **`cedar-artifact-mcp`**.
- Upload the instance to CEDAR.

### Step 4 — Create the study in Canopy
Create a new study in Canopy, **bootstrapping it with the CEDAR Study instance from Step 1**, with files attached.
- `study-metadata.json` (from Step 1) pre-fills the study fields — the *Create Study* page gets a button to upload it.

```
researcher's artifacts (xlsx + pdfs)   ── any input; synthetic study = example
        │
        ▼
[Step 1] fill Canopy Study instance  ◄── pull Study template from CEDAR
        │                                   (this instance bootstraps Step 4)
        ▼
[Step 2] design domain template      ──► CEDAR
        │
        ▼
[Step 3] fill domain instance        ◄── pull domain template from CEDAR
        │
        ▼
[Step 4] create study in Canopy ◄── bootstrap from Step 1 instance + attach files
```

## The deliverable

The primary deliverable is a **reusable AI artifact that drives the [4-step workflow](#workflow) generically** — give it any researcher's datasets and documents, and it produces valid CEDAR metadata and a bootstrapped Canopy study. Deciding its form is the first task of the CoFest:

| Form | Fit | Notes |
|---|---|---|
| **Claude Skill** | Strong candidate | Packages the workflow as instructions + scripts that invoke the CEDAR MCP servers; installable and shareable; runs the same steps every time. |
| **Claude Project** | Strong candidate | Bundles the system prompt, the CEDAR MCP connections, and reference files (templates, examples) so a researcher just drops in their artifacts. |
| **Claude MCP** | Probably not | The CEDAR capabilities are *already* MCP servers; wrapping them in another MCP mostly adds a layer. The deliverable should orchestrate the existing servers, not duplicate them. |

Whatever the form, success is: **a researcher with no CEDAR expertise runs the artifact on their own data and gets a registered, FAIR Canopy study.** We'll prove it on the bundled example.

Supporting deliverables produced along the way (first-class outputs in their own right):

- A filled **Canopy Study instance** (Step 1) and a **domain-specific template + filled instance** (Steps 2–3), as CEDAR JSON-LD — generated from the example study.
- Documentation: this README + the step-by-step [`docs/RUNBOOK.md`](docs/RUNBOOK.md).

## What we provide (example input data)

The bundled **synthetic study** is just an *example input* so contributors can build and test the artifact immediately — the deliverable must generalize beyond it. Under [`data/synthetic-study/`](data/synthetic-study/):

- A **dataset spreadsheet** (`.xlsx`) of subject-level measurements + a **data dictionary** sheet.
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
├── src/                       ← the deliverable (Skill/Project) + helper scripts; data generator lives here too
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
3. **Grab the example data** — the synthetic study in [`data/synthetic-study/`](data/synthetic-study/) to build and test against.
4. **Build the deliverable** and drive [Steps 1–4](#workflow); see [`docs/RUNBOOK.md`](docs/RUNBOOK.md).

## Who should join

Developers and researchers interested in open biomedical data, metadata standards, FAIR data hubs, schema-driven software, ontologies, and practical uses of AI in open science. Comfort with Python, JSON/JSON-LD, or LLM tooling helps, but there's room at every level — parsing, extraction, validation, ontology mapping, and UI all need hands.

## Team

| Name | Role | Affiliation |
|---|---|---|
| Atti L. Egyedi | Project lead / main contact | Stanford University |
| Martin O'Connor | Workflow & pipeline design | Stanford University |
| Marcos Martínez Romero | Canopy / project concept | Stanford University |
| Matthew Horridge | Canopy / senior advisor | Stanford University |

*Contributors welcome — open an issue or say hello at the CoFest.*

## Links

- **Canopy (code):** <https://github.com/canopy-datahub>
- **Canopy (production):** <https://canopy.stanford.edu/>
- **Canopy (staging):** <https://staging.canopyplatform.org/>
- **NIH RADx Data Hub (paper):** <https://publichealth.jmir.org/2025/1/e72677/>
- **NIH RADx Data Hub (website):** <https://radxdatahub.nih.gov/>
- **CEDAR Workbench:** <https://cedar.metadatacenter.org/>
- **CEDAR Artifact MCP:** <https://github.com/metadatacenter/cedar-artifact-mcp>
- **BioPortal Term MCP:** <https://github.com/metadatacenter/bioportal-term-mcp>

## License

[GPL-3.0](LICENSE).
