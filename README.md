# Canopy: AI-Assisted Metadata Generation

### CollaborationFest 2026 project - [CoFest 2026](https://www.open-bio.org/events/bosc-2026/collaborationfest/)

Work out an **AI-assisted way to describe research data** — turning a researcher's ordinary artifacts (spreadsheets, data dictionaries, protocols, papers) into standards-compliant CEDAR metadata and a registered Canopy study, with a human in the loop. The tangible output of the CoFest is a **set of prompts and strategies, plus a short lessons-learned writeup**, that drive a four-step workflow over our CEDAR Model Context Protocol (MCP) servers — and, as an extension, a reusable Claude Skill. **Bring your own LLM** (Claude, ChatGPT, Gemini, …); we don't provide a license. The aim: register FAIR-aligned studies in minutes instead of hours.

---

## At a glance: your CoFest roadmap

Use this as your map. Start with **Dependencies**, do the **Basic track** (the core two-day goal), and reach for the **Advanced track** if you have time. Details for each item are linked.

**① Dependencies — set up once ([details](#getting-started))**

- [ ] Create accounts + API keys for [CEDAR](https://cedar.metadatacenter.org/) and [BioPortal](https://bioportal.bioontology.org/)
- [ ] Install the toolchains the servers need: **Java + Maven** (three servers) and **`uv`** (Python, for `bioportal-term-mcp` only) — see [Prerequisites](#prerequisites-and-dependencies)
- [ ] [Install the CEDAR MCP servers](#installing-the-mcp-servers) and connect them to your LLM client
- [ ] Bring an LLM you can use (Claude, ChatGPT, Gemini, …) — we don't provide a license

**② Basic track — the core two-day goal**

- [ ] [Step 1](#step-1--fill-out-the-existing-canopy-study-template) — fill the Canopy Study template from the example artifacts
- [ ] [Step 2](#step-2--create-a-domain-specific-template) — design a domain-specific template
- [ ] [Step 3](#step-3--fill-the-domain-specific-template) — fill it (a valid instance)
- [ ] [Step 4](#step-4--create-the-study-in-canopy) — create the study in Canopy
- [ ] **Capture your prompts** and **write up lessons learned** — the [primary deliverable](#the-deliverable)

**③ Advanced track — extensions**

- [ ] Package the workflow as a reusable **Claude Skill** that submits data + creates the study
- [ ] Run the same prompts across different LLMs and compare
- [ ] Add confidence / provenance to inferred fields, or evaluate on a held-out study

---

## Background

[Canopy](https://github.com/canopy-datahub) is an open-source platform for building FAIR-aligned scientific data hubs, derived from the [NIH RADx Data Hub](https://radxdatahub.nih.gov/) and powered by [CEDAR](https://cedar.metadatacenter.org/) metadata templates.

A common barrier for data contributors is the effort required to complete structured metadata forms by hand before a study or data file can be registered. Filling these forms is slow, error-prone, and intimidating — the "blank page" problem — and it is one of the biggest reasons otherwise valuable datasets never get described well enough to be found and reused.

In this CoFest project we will prototype an **AI-assisted workflow** that reads common research artifacts (CSV/Excel files, data dictionaries, supplementary PDFs, protocols, grants, papers) and generates **draft CEDAR-compatible metadata for human review**. The goal is not to replace expert curation, but to reduce blank-page friction, suggest likely values, anchor those values to real ontology terms, and make metadata submission faster and more consistent.

A natural foundation for this work is the set of **CEDAR MCP servers** we maintain — focused tool servers that let an LLM use CEDAR directly, without each AI integration having to reinvent the wiring (see [About Canopy and CEDAR](#about-canopy-and-cedar) and [MCP Servers](#mcp-servers-the-foundation) below).

## Goals

The point of the CoFest is **developing and understanding** how to drive metadata description with AI — not shipping a finished product. So the tangible output is **prompts, strategies, and a lessons-learned document**, not (necessarily) software. The bundled synthetic study is only an example input; whatever you develop should generalize to *any* researcher's datasets and documents.

### Core goals (the 2-day focus)

1. **Drive the [4-step workflow](#workflow) with an LLM of your choice** — fill the Canopy Study template, design a domain-specific template, fill it, and create the study in Canopy — using the CEDAR MCP servers.
2. **Capture the prompts and strategies that worked** — the prompts, the order of operations, what to feed the model, where it goes wrong, and how to recover. This is the primary deliverable.
3. **Write up lessons learned** — a short document distilling what works, what doesn't, and recommendations for doing this reliably and generically.
4. **Prove it on the example.** Run your approach against the bundled [synthetic study](#what-we-provide-example-input-data) and show the four steps complete end-to-end.

### Extensions / stretch goals

- **Package it as a reusable [Claude Skill](#the-deliverable)** that submits the data and creates the study, so others can run it in one step.
- Confidence scores / provenance on each inferred field, so reviewers know what to check first.
- Evaluate against a held-out study to measure how much manual effort the approach actually saves.
- Try the same prompts across different LLMs (Claude, ChatGPT, Gemini) and compare.

## About Canopy and CEDAR

If you're new to these systems, here's the context you need before the rest of the proposal makes sense.

**Canopy** is open-source, generalist **repository infrastructure**: it lets a researcher register a *study* and submit both its **data files** and the **metadata** that describes them, then makes the result findable and downloadable by others according to an access policy. It is derived from the NIH RADx Data Hub and is the platform our metadata ultimately lands in. Every Canopy submission is organized around a study, and Canopy ships with a **generic study-metadata template** that every study must fill in (title, investigators, design, and so on) — this is the "Canopy Study template" referenced throughout this document.

**CEDAR** (the Center for Expanded Data Annotation and Retrieval) is the metadata engine underneath. Two CEDAR concepts matter here. A **template** is a reusable blueprint that defines *what* metadata to capture — its fields, their data types, and which values are allowed (for example, that a "country" field must come from a controlled list, or that a date field must be a real date). An **instance** is a single record that has been *filled in* against a template — the actual values for one study or one dataset. A template is the empty form; an instance is the completed form. CEDAR instances are stored as JSON-LD, so a "valid instance" is one whose values conform to its template.

Putting it together, the **common workflow** is: a researcher has data they want to share; before it can be submitted they must describe it — locate the data, extract the relevant facts, and define the structure that captures them. They then go to **Canopy to submit** the study and its files, and lean on **CEDAR to describe** everything properly with templates and instances. The friction is in that description step, and that is exactly what this project tries to assist with AI — and, as an extension, what a Skill could automate end-to-end: describe the data, create the study, and submit.

## MCP Servers (the foundation)

The work builds **on top of** a set of [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) servers for CEDAR — you orchestrate them, you don't replace them. MCP is an open standard — think of it as a universal adapter that lets an AI assistant call external tools and data sources in a uniform way; an MCP *server* exposes a specific capability (here, a slice of CEDAR or BioPortal) as a set of callable tools. Because MCP is a shared standard, the same servers work across MCP-capable clients — Claude, ChatGPT, and others — so you can bring whatever LLM you have a license for. Each server is **self-documenting**: connect it to your client and it advertises its own tools and parameters, and each repository's README explains setup and usage in detail — start there.

| MCP server                                                                             | Runtime | What it does                                                                                                                    |
|----------------------------------------------------------------------------------------|--|---------------------------------------------------------------------------------------------------------------------------------|
| [`cedar-artifact-mcp`](https://github.com/metadatacenter/cedar-artifact-mcp)           | **Java** | Author and validate CEDAR templates and metadata instances **in memory** — build templates/fields/elements, fill instances, convert between YAML and CEDAR JSON. |
| [`bioportal-term-mcp`](https://github.com/metadatacenter/bioportal-term-mcp)           | **Python (`uv`)** | Look up ontology terms in BioPortal so values are anchored to real, standard identifiers (IRIs) instead of guessed free text. |
| [`cedar-artifact-rest-mcp`](https://github.com/metadatacenter/cedar-artifact-rest-mcp) | **Java** | The I/O counterpart to `cedar-artifact-mcp`: **persist and fetch** artifacts on a live CEDAR server (create / get / update / delete / server-side validate). |
| [`cedar-cee-mcp`](https://github.com/metadatacenter/cedar-cee-mcp)                     | **Java** | **Show a template or instance as a form** in the browser — read-only to review, or editable so a person fills it in (via the CEDAR Embeddable Editor), with the result flowing back. |

All four are public — see [Links](#links). Treat each repo's own README as the source of truth for setup. The one runtime split worth noting: **only `bioportal-term-mcp` runs on Python (`uv`)** — the other three are **Java** (and `cedar-artifact-mcp` additionally needs a local build of `cedar-artifact-library`, per its README).

> **API keys:** Working against live CEDAR and BioPortal requires free accounts and API keys. See [Getting Started](#getting-started). Never commit keys — `.gitignore` already excludes the usual files.

## Workflow

The workflow has two halves: first **describe** the study with CEDAR (Steps 1–3), then **submit** it to Canopy (Step 4). Steps 1–3 each produce a CEDAR artifact; Step 4 turns those into a live study. The whole thing runs over the [MCP servers](#mcp-servers-the-foundation), driven by an LLM.

**Input (Step 0):** the researcher's artifacts — datasets (XLSX/CSV, relational exports) and documents (papers, protocol, grant, SOP, supplementary PDFs). The bundled synthetic study is one example; the approach must work for any.

### Step 1 — Fill out the existing Canopy Study template
*What:* produce a filled **Canopy Study** instance from the artifacts. *Why:* every Canopy submission is built around a study, and Canopy provides a single generic study-metadata template (title, investigators, design, dates, …) that every study must populate. Filling it is the unavoidable first step, and an LLM can draft most of it by reading the protocol and dataset rather than the researcher typing it by hand. This instance also **bootstraps the study in Step 4**, so it's worth getting right first.
- The Canopy Study template is an existing CEDAR template (readable mirror in [`templates/`](templates/)); pull it live from its well-known CEDAR location with **`cedar-artifact-rest-mcp`**.
- Fill a valid instance from the PDFs/datasets with **`cedar-artifact-mcp`**, anchoring controlled values via **`bioportal-term-mcp`**.

### Step 2 — Create a domain-specific template
*What:* design a new CEDAR template that captures the metadata specific to *this* study's data (target shape in [`templates/domain-specific-template.yaml`](templates/domain-specific-template.yaml)). *Why:* the generic Study template describes the study, but not the particulars of the dataset — its condition, assays, organism, units, identifiers. A domain-specific template captures those, and crucially it constrains key fields to **controlled terms** so values are interoperable. A *controlled term* is a value drawn from an agreed vocabulary (an ontology) instead of free text — so "prediabetes" resolves to one canonical concept rather than a dozen spellings. **BioPortal** is the repository of biomedical ontologies those terms come from; the `bioportal-term-mcp` server looks them up. Controlled terms are what make a dataset findable and comparable across studies.
- Author the template with **`cedar-artifact-mcp`**; resolve controlled terms with **`bioportal-term-mcp`**.
- Upload it to CEDAR with **`cedar-artifact-rest-mcp`**; view/verify with **`cedar-cee-mcp`** or the CEDAR UI.

### Step 3 — Fill the domain-specific template
*What:* create a **valid instance** of the Step 2 template. *Why:* a template is just the empty form — the actual descriptive metadata only exists once it's filled in and conforms to the template (right field types, allowed values, required fields present). A *valid* instance is one CEDAR accepts as conforming; validity is what lets Canopy trust and publish the metadata downstream.
- Pull the Step 2 template back from CEDAR.
- Infer values from the artifacts and build the instance with **`cedar-artifact-mcp`**; upload it to CEDAR.

### Step 4 — Create the study in Canopy
*What:* register a new study in Canopy, **bootstrapping it from the Step 1 Study instance**, and attach the files. *Why:* this is where description becomes a real, shareable record — the point of the whole exercise. Instead of re-keying everything into the Canopy *Create Study* form, the Step 1 metadata pre-fills it.
- `study-metadata.json` (from Step 1) pre-fills the study fields — the *Create Study* page gets a button to upload it.
- The submission then follows Canopy's normal [Submission Workflow](#submission-workflow), and what others can see is governed by [Access Control](#access-control).

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

## Submission Workflow

Step 4 lands in Canopy's standard submission flow, so it helps to know how that works. Full walkthrough: [Canopy tutorial → Submission Workflow](https://canopy.stanford.edu/tutorial?tutorial=submissionWorkflow).

Getting data onto the platform involves two roles: a **Data Submitter**, who registers a study and uploads its files, and a **Data Curator**, who reviews the submission and approves or rejects it. A submission is only published after a curator reviews it — the author and the reviewer are deliberately different people. (An **Application Administrator** grants roles and manages the system.)

A study must exist before any files can be uploaded, so the flow is: **register the study** (and set its access level) → **create a submission and upload files** → **bundle** related files (a data file with its metadata and data dictionary) → **validate** (Canopy checks each bundle against the required metadata template and data-dictionary spec) → **review and submit**. The package is then read-only while the curator approves or rejects files (with a reason); on approval it's published per the study's access level, and both sides are notified by email. A completed submission isn't edited in place — to update data you start a new submission, and re-uploading a same-named file creates a new version, preserving history.

This matters for the project: the metadata our workflow produces is exactly what Canopy validates at the **validate** step, so well-formed CEDAR instances are what make a submission pass cleanly.

## Access Control

What others can see of a submitted study is governed by its access level. Full detail: [Canopy tutorial → Data Access Control](https://canopy.stanford.edu/tutorial?tutorial=dataAccessControl).

Access is set **per study** (it applies to the study's metadata and all its files), with three levels:

| Access level | Who can see the study and download its files |
|---|---|
| **Public** | Everyone, including visitors who aren't logged in. |
| **Limited** | Any logged-in user. |
| **Private** | Only the study's creator, plus Curators and Administrators. |

Newly registered studies default to **Public**, so set the level deliberately before sharing. It can be changed at any time by the study's creator, a curator, or an administrator, and is enforced everywhere a study is exposed — search/browse, the study overview, and every file download. (One nuance: variable-level *descriptions* can surface in variable search even for restricted studies, but the underlying data files stay protected.)

## The deliverable

The **primary deliverable is knowledge, captured as artifacts you can reuse** — not finished software. Concretely, by the end of the two days we want:

1. **A curated set of prompts** that drive [Steps 1–4](#workflow) with an LLM — the prompts themselves, the order to run them, what context to feed in, and the guardrails that keep the model on track.
2. **A lessons-learned document** — what worked, what didn't, where models go wrong (and how to recover), and recommendations for doing this reliably and *generically* across different inputs and different LLMs.
3. **The worked example** — the filled Canopy Study instance (Step 1) and the domain-specific template + instance (Steps 2–3), as CEDAR JSON-LD, produced from the bundled study, plus a registered study in Canopy.

**Prerequisite — bring your own LLM.** You need access to an LLM with tool/MCP support (Claude, ChatGPT, Gemini, …); we don't provide a license. Because the MCP servers are an open standard, the same prompts and servers should work across clients — comparing them is a welcome bonus.

**Extension — a Claude Skill.** Teams who get the workflow running smoothly can package it as a reusable [Claude Skill](https://modelcontextprotocol.io/) that creates the study and submits the data in one step. That turns the prompts-and-strategies knowledge into something installable. It's the natural "next step," not the day-one goal.

Success looks like: **someone who isn't a CEDAR expert can follow your prompts and lessons-learned on their own data and end up with a registered, FAIR Canopy study.**

## What we provide (example input data)

The bundled **synthetic study (SPbE-2026)** is just an *example input* so you can build and test immediately — your approach must generalize beyond it. Under [`data/synthetic-study/`](data/synthetic-study/):

- **`SPbE-2026_dataset.xlsx`** — 40 subjects × 20 columns, plus a `data_dictionary` sheet. The same data is also provided as **`SPbE-2026_dataset.csv`** (open format, no licensing concerns).
- **`SPbE-2026_protocol.pdf`** — a ~10-page study protocol (rich free text to extract from).
- **`SPbE-2026_SOP_sample-collection.pdf`** — a supplementary SOP.

The dataset columns deliberately span varied CEDAR field types — numeric, date, boolean, ontology-controlled, and external-identifier — so the example exercises real metadata, not 20 strings:

| Column | Type | Controlled by / authority |
|---|---|---|
| `subject_id` | string | — |
| `enrollment_date`, `visit_date` | date | ISO-8601 |
| `age_years`, `bmi_kg_m2`, `baseline_glucose_mg_dl`, `week12_glucose_mg_dl`, `hba1c_pct`, `systolic_bp_mmhg`, `adherence_pct` | numeric | — |
| `sex` | controlled | NCIT |
| `country` | controlled | GAZ / ISO-3166 |
| `condition` | controlled | MONDO |
| `study_arm` | controlled | NCIT (study arm) |
| `on_glucose_medication`, `adverse_event`, `completed_study` | boolean | — |
| `investigator_orcid` | identifier | ORCID |
| `reference_pmid` | identifier | PubMed ID |
| `protocol_doi` | identifier | DOI |

These are AI-generated and entirely fictional — no real subjects or results. Regenerate with `python3 src/gen_data.py`.

## Repository structure

```
canopy-metadata-cofest-2026/
├── README.md                  ← this proposal
├── LICENSE                    ← GPL-3.0
├── .gitignore
├── data/
│   └── synthetic-study/       ← example study: dataset (xlsx + csv), dictionary, 10-pg protocol, SOP
├── templates/                 ← Canopy Study template + domain-specific template (CEDAR + YAML mirrors)
├── src/                       ← prompts/strategies, helper scripts, optional Skill; data generator lives here
├── docs/                      ← runbook + (to come) the prompts and lessons-learned writeup
└── images/                    ← diagrams / screenshots
```

## Getting Started

> Detailed, step-by-step instructions live in [`docs/RUNBOOK.md`](docs/RUNBOOK.md). Work through the setup below in order; it maps to **① Dependencies** in the [roadmap](#at-a-glance-your-cofest-roadmap).

### Prerequisites and dependencies

The CEDAR MCP servers run locally, so you need their toolchains installed before you can connect them:

- **Java (17+) and Maven** — required for the three JVM-based servers (`cedar-artifact-mcp`, `cedar-artifact-rest-mcp`, `cedar-cee-mcp`). Note `cedar-artifact-mcp` also needs a local build of `cedar-artifact-library` — see its README.
- **[`uv`](https://docs.astral.sh/uv/)** (with Python 3.11+) — needed for the one Python server, **`bioportal-term-mcp`**.
- **An LLM client with MCP/tool support** — Claude, ChatGPT, Gemini, etc. **Bring your own license; we don't provide one.**

> Each server's repo lists its exact requirements — treat those as the source of truth. If you'd rather not install by hand, your LLM/AI assistant can often install Java and `uv` and wire up the servers for you; just ask it to.

### Accounts & API keys

Create free accounts and generate API keys, then export them as environment variables (`CEDAR_API_KEY`, `BIOPORTAL_API_KEY`). **Never commit keys** — `.gitignore` already excludes the usual files.

- CEDAR: <https://cedar.metadatacenter.org/>
- BioPortal (for `bioportal-term-mcp`): <https://bioportal.bioontology.org/>

### Installing the MCP servers

The [four MCP servers](#mcp-servers-the-foundation) are **self-documenting** — each repository's README is the authoritative install/usage guide. The short version: clone each server and build/install per its README — `mvn package` for the three Java servers (`cedar-artifact-mcp`, `cedar-artifact-rest-mcp`, `cedar-cee-mcp`), `uv sync` for the one Python server (`bioportal-term-mcp`) — then **register each with your LLM client** (e.g. in `~/.claude.json`) so it can call their tools. Confirm the tools appear in your client before moving on.

### Run

1. **Grab the example data** — the synthetic study in [`data/synthetic-study/`](data/synthetic-study/).
2. **Drive [Steps 1–4](#workflow)** with your LLM (see [`docs/RUNBOOK.md`](docs/RUNBOOK.md)), and **capture the prompts and lessons learned** as you go — that's the deliverable.

## Who should join

Developers and researchers interested in open biomedical data, metadata standards, FAIR data hubs, schema-driven software, ontologies, and practical uses of AI in open science. Comfort with Python, JSON/JSON-LD, or LLM tooling helps, but there's room at every level — parsing, extraction, validation, ontology mapping, and UI all need hands.

## Team

| Name | Role | Affiliation |
|---|---|---|
| Attila L. Egyedi | Project lead / main contact | Stanford University |
| Martin O'Connor | Workflow & pipeline design | Stanford University |
| Marcos Martínez Romero | Canopy / project concept | Stanford University |
| Matthew Horridge | Canopy / senior advisor | Stanford University |

*Contributors welcome — open an issue or say hello at the CoFest.*

## Links

- **Canopy (code):** <https://github.com/canopy-datahub>
- **Canopy (production):** <https://canopy.stanford.edu/>
- **Canopy tutorial — Submission Workflow:** <https://canopy.stanford.edu/tutorial?tutorial=submissionWorkflow>
- **Canopy tutorial — Data Access Control:** <https://canopy.stanford.edu/tutorial?tutorial=dataAccessControl>
- **NIH RADx Data Hub (paper):** <https://publichealth.jmir.org/2025/1/e72677/>
- **NIH RADx Data Hub (website):** <https://radxdatahub.nih.gov/>
- **CEDAR Workbench:** <https://cedar.metadatacenter.org/>
- **Model Context Protocol:** <https://modelcontextprotocol.io/>
- **CEDAR Artifact MCP** (Java): <https://github.com/metadatacenter/cedar-artifact-mcp>
- **BioPortal Term MCP** (Python / `uv`): <https://github.com/metadatacenter/bioportal-term-mcp>
- **CEDAR Artifact REST MCP** (Java): <https://github.com/metadatacenter/cedar-artifact-rest-mcp>
- **CEDAR CEE MCP** (Java): <https://github.com/metadatacenter/cedar-cee-mcp>

## License

[GPL-3.0](LICENSE).
