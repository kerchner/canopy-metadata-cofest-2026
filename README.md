# Canopy: AI-Assisted Metadata Generation

### CollaborationFest 2026 Project - [CoFest 2026](https://www.open-bio.org/events/bosc-2026/collaborationfest/)

This project is part of **[Canopy](https://github.com/canopy-datahub)**, an open-source platform for building FAIR-aligned scientific data hubs that support data sharing, harmonization, discovery, and reuse across research studies.

Researchers must describe their studies with structured metadata before data can be shared and discovered. In Canopy, this metadata is created using **[CEDAR](https://cedar.metadatacenter.org/)**, an open-source platform for designing and managing machine-readable metadata templates, which define what information to capture and enforce standardized metadata.

Canopy organizes data around **studies**. Each study consists of one or more data files together with structured metadata describing the study, its datasets, and related resources. This metadata is captured using reusable CEDAR templates, making studies easier to discover, understand, and reuse.

Creating this metadata is still largely a manual process. Researchers often work from spreadsheets, data dictionaries, protocols, and publications, then spend considerable time translating that information into structured metadata.

This project explores AI-assisted approaches for generating structured metadata directly from research artifacts, reducing manual effort. As part of the project, we will also explore how this metadata can be used to populate and register studies in Canopy.

## Project Goals?

## Environment Setup

Before jumping into the tutorial and project, please complete the environment setup by following the instructions on [this page](https://github.com/canopy-datahub/canopy-metadata-cofest-2026/blob/main/INSTALL.md). Once everything is set up, come back here to continue.

## Tutorial

Before starting the project, complete this short tutorial to verify that your environment is working correctly and to become familiar with the core concepts.

In this tutorial, you'll learn the basics of creating metadata with **CEDAR**, the metadata platform used by Canopy. A **CEDAR template** defines the metadata fields to be captured (for example, title, authors, or publication date), while an **instance** is a completed metadata record created from that template.

To interact with CEDAR and BioPortal, you'll use several **MCP (Model Context Protocol) servers**, which allow your LLM to create, validate, visualize, and store metadata through external tools.

### MCP Servers

| MCP server | Purpose |
|------------|---------|
| [`cedar-artifact-mcp`](...) | Create and validate CEDAR templates and metadata instances. |
| [`bioportal-term-mcp`](...) | Search BioPortal for ontology terms and controlled vocabulary values. |
| [`cedar-artifact-rest-mcp`](...) | Upload, retrieve, and manage templates and instances on a CEDAR server. |
| [`cedar-cee-mcp`](...) | Visualize templates and instances as interactive forms using the CEDAR Embeddable Editor. |


### Task

Create a simple **publication metadata template** using the MCPs you just configured. Your template should include:

- Title
- Authors (including their ORCID identifiers)
- Publication date
- Publication type (use a controlled vocabulary linked to the [SIO "publication" term](https://bioportal.bioontology.org/ontologies/SIO?p=classes&conceptid=http%3A%2F%2Fsemanticscience.org%2Fresource%2FSIO_000087) in BioPortal)
- Keywords

Once your template is complete:

1. Find a journal article and use an LLM to generate a metadata instance for your template.
2. Open the generated instance using **CEE-MCP** to verify that it renders correctly.
3. Use the appropriate MCPs to upload both the template and the instance to CEDAR.

## Project Goals

The goal of this CoFest project is to explore reusable AI-assisted workflows for metadata generation.

Rather than building a single solution for one dataset, we encourage participants to experiment with prompting strategies, pipelines, and agentic workflows that can generalize across different studies and research domains.

Possible directions include:

- Designing reusable prompting strategies for metadata generation.
- Building multi-step AI workflows or agentic pipelines.
- Evaluating different LLMs, tools, and prompting techniques.
- Exploring how generated metadata can be integrated into Canopy.

## Example Workflow

To provide a common starting point, we include a [synthetic study](data/synthetic-study) that can be used to evaluate an end-to-end AI-assisted metadata generation workflow. This workflow is only an example—you are encouraged to adapt, extend, or replace it with your own reusable approach.

### Step 1 — Generate a Canopy Study Metadata Instance

Canopy provides a generic **Canopy Study Template** that captures the study-level metadata required for every submission. Start by retrieving this existing template from CEDAR using `cedar-artifact-rest-mcp` using the template ID provided, then generate a completed metadata instance from the provided study materials.

**Template:** [Canopy Study Template](https://openview.metadatacenter.org/templates/https:%2F%2Frepo.metadatacenter.org%2Ftemplates%2Faff00b59-0bb7-4e40-9437-3216e5fb0ff7)

**Template ID**
```text
https://repo.metadatacenter.org/templates/aff00b59-0bb7-4e40-9437-3216e5fb0ff7
```

### Step 2 — Design a Domain-Specific Metadata Template

Create a new CEDAR template describing the metadata specific to the provided dataset. Choose appropriate field types and, where appropriate, controlled vocabulary terms from BioPortal.

### Step 3 — Generate a Metadata Instance

Populate the template created in Step 2 using information extracted from the provided datasets and documents.


### Step 4 — Register the Study in Canopy *(Optional)*

Use the generated metadata to populate a study in Canopy. This demonstrates how AI-generated metadata can support the complete submission workflow.

## Deliverables

The primary outcome of this project is reusable knowledge that others can build upon.

Examples of useful deliverables include:

- Reusable prompts for metadata generation.
- AI workflows or pipelines that can be applied to multiple studies.
- Agentic workflows combining MCP servers and LLMs.
- Lessons learned, best practices, and common pitfalls.
- (Optional) A study registered in Canopy using the generated metadata.

## Get Going

> 1. **🍴 Fork this repo, then clone your fork** to your machine.
> 2. **📂 Work in the `work/` folder.** Keep everything you produce there.
> 3. **⚙️ Install the tools and servers** — open the **👉 [setup guide](INSTALL.md)** and follow it.

## Team

| Name | Role | Affiliation |
|---|---|---|
| Attila L. Egyedi | Project lead / main contact | Stanford University |
| Martin O'Connor | Workflow & pipeline design | Stanford University |
| Marcos Martínez Romero | Canopy / project concept | Stanford University |
| Matthew Horridge | Canopy / senior advisor | Stanford University |

## Links

| Resource | Link |
|---|---|
| Canopy (code) | <https://github.com/canopy-datahub> |
| Canopy (production) | <https://canopy.stanford.edu/> |
| Canopy tutorial — Submission Workflow | <https://canopy.stanford.edu/tutorial?tutorial=submissionWorkflow> |
| Canopy tutorial — Data Access Control | <https://canopy.stanford.edu/tutorial?tutorial=dataAccessControl> |
| NIH RADx Data Hub (paper) | <https://publichealth.jmir.org/2025/1/e72677/> |
| NIH RADx Data Hub (website) | <https://radxdatahub.nih.gov/> |
| CEDAR Workbench | <https://cedar.metadatacenter.org/> |
| Model Context Protocol | <https://modelcontextprotocol.io/> |
| MCP install guide | [INSTALL.md](INSTALL.md) |
| CEDAR Artifact MCP (Java) | <https://github.com/metadatacenter/cedar-artifact-mcp> |
| BioPortal Term MCP (Python / `uv`) | <https://github.com/metadatacenter/bioportal-term-mcp> |
| CEDAR Artifact REST MCP (Java) | <https://github.com/metadatacenter/cedar-artifact-rest-mcp> |
| CEDAR CEE MCP (Java) | <https://github.com/metadatacenter/cedar-cee-mcp> |

## License

[GPL-3.0](LICENSE).
