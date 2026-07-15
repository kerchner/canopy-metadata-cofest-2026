# Canopy: AI-Assisted Metadata Generation

### CollaborationFest 2026 Project - [CoFest 2026](https://www.open-bio.org/events/bosc-2026/collaborationfest/)

This project is part of **[Canopy](https://github.com/canopy-datahub)**, an open-source platform for building FAIR-aligned scientific data hubs that support data sharing, harmonization, discovery, and reuse across research studies.

In Canopy, researchers organize and share data as studies, each consisting of one or more datasets together with structured metadata describing the study, its datasets, and related resources. This metadata is authored using **[CEDAR](https://cedar.metadatacenter.org/)**, an open-source platform for designing and managing machine-readable metadata templates.

Creating high-quality metadata is still largely manual. Researchers often extract information from datasets, data dictionaries, protocols, and publications, then translate it into structured metadata. This project explores AI-assisted approaches for automating parts of that process while maintaining high-quality metadata that can be used in Canopy. As a bonus part, we will also explore how this metadata can be used to populate and register studies in Canopy.

## Project Goals

The goal of this CoFest project is to explore reusable AI-assisted workflows for metadata generation.

Rather than building a workflow tailored to a single dataset, we encourage participants to experiment with prompting strategies, pipelines, and agentic workflows that can be reused across different studies and research domains.

Participants are encouraged to explore ideas such as:

- Designing reusable prompting strategies for metadata generation.
- Developing reusable metadata generation workflows that can be applied across studies and research domains.
- Evaluating different LLMs, tools, and prompting techniques.
- Exploring how generated metadata can be integrated into Canopy.

Before diving into the project, we'll first set up the development environment and complete a short tutorial covering the core concepts used throughout the rest of the project.

## Environment Setup

Before jumping into the tutorial and project, please complete the environment setup by following the instructions on [this page](https://github.com/canopy-datahub/canopy-metadata-cofest-2026/blob/main/INSTALL.md). Once everything is set up, come back here to continue.

## Tutorial

Before starting the project, complete this short tutorial to verify that your environment is set up correctly and to become familiar with the core concepts.

In this tutorial, you'll learn the basics of creating metadata with **CEDAR**, the metadata platform used by Canopy. A **CEDAR template** defines the metadata fields to be captured (for example, title, authors, or publication date), while an **instance** is a completed metadata record created from that template.

To complete the tutorial, you'll use the **MCP (Model Context Protocol) servers** you just configured. These servers allow your LLM to interact with CEDAR and BioPortal to create, validate, visualize, and store metadata. The MCP servers used in this project are summarized below.

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

## Project Tasks and Example Workflow

To provide a common starting point, we include a [synthetic study](data/synthetic-study) that can be used to evaluate an end-to-end AI-assisted metadata generation workflow. This workflow is only an example—you are encouraged to adapt, extend, or replace it with your own reusable approach.

### Project Task 1 — Populate the existing Canopy study template

Canopy provides a generic **Canopy Study Template** that captures the study-level metadata required for every submission. Start by retrieving this existing template from CEDAR using `cedar-artifact-rest-mcp` using the template ID provided, then generate a completed metadata instance from the provided study materials.

**Template:** [Canopy Study Template](https://openview.metadatacenter.org/templates/https:%2F%2Frepo.metadatacenter.org%2Ftemplates%2Faff00b59-0bb7-4e40-9437-3216e5fb0ff7)

**Template ID**
```text
https://repo.metadatacenter.org/templates/aff00b59-0bb7-4e40-9437-3216e5fb0ff7
```

### Project Task 2 — Design a domain-specific metadata template

Create a new CEDAR template describing the metadata specific to the provided dataset. Choose appropriate field types and, where appropriate, controlled vocabulary terms from BioPortal.

### Project Task 3 — Populate your domain-specific template

Populate the template created in Step 2 using information extracted from the provided datasets and documents.

### Optional Task 4 — Register the s tudy in Canopy

Use the generated metadata to populate a study in Canopy. This demonstrates how AI-generated metadata can support the complete submission workflow.

## Deliverables

The primary deliverable is a reusable AI workflow and reusable knowledge that others can build upon.

Examples of useful deliverables include:

- Reusable prompts for metadata generation.
- AI workflows or pipelines that can be applied to multiple studies.
- Agentic workflows combining MCP servers and LLMs.
- Lessons learned, best practices, and common pitfalls.
- (Optional) A study registered in Canopy using the generated metadata.

## Get Going

> 1. **🍴 Fork this repo, then clone your fork** to your machine.
> 2. **📂 Work in the `work/` folder.** Keep everything you produce there.
> 3. **⚙️ If you followed the turorial tools and servers should already be installed but if not:** — open the **👉 [setup guide](INSTALL.md)** and follow it.

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
