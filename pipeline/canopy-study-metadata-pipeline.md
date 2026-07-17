# Canopy Study Metadata Pipeline — Prompt Playbook

A reusable, LLM-driven pipeline for turning a study's metadata (from a **local file** or a **URI**) into a validated **CEDAR instance** built on the **Canopy Study Metadata** template, uploaded to CEDAR, and exported as **JSON/YAML** for loading into Canopy.

This is a *prompt playbook*: the work is done by an MCP-capable LLM (Claude, ChatGPT, etc.) calling the CEDAR/BioPortal MCP servers. Copy the prompts in order, or paste the whole "One-shot driver prompt" at the end.

---

## 1. What you need before you start

**MCP servers (must be configured in your LLM client):**

| Server | Role in this pipeline |
|---|---|
| `cedar-artifact` | Build, render, and **validate** instances locally (no server calls). |
| `cedar-artifact-rest` | **Upload** the instance to the CEDAR server (requires API key). |
| `bioportal-term` | Resolve controlled-vocabulary terms (only if you add ontology-bound fields). |

**CEDAR API key (required — this pipeline always uploads):**

1. Sign in at <https://cedar.metadatacenter.org/>.
2. Open your **Profile** (top-right) → copy your **API Key**.
3. Put it in the `cedar-artifact-rest` MCP server configuration as the server expects
   (typically an env var such as `CEDAR_API_KEY`, or an `Authorization: apiKey <key>` header).
   Do **not** paste the key into chat prompts — the server reads it from its own config.
4. Verify connectivity by asking the LLM: *"Ping the cedar-artifact-rest server."*

**The template this pipeline targets:**

```
Template name: Canopy Study Metadata Specification v2
Template ID:   https://repo.metadatacenter.org/templates/aff00b59-0bb7-4e40-9437-3216e5fb0ff7
```

> The uploaded instance's `schema:isBasedOn` **must** be this exact template ID.

---

## 2. Pipeline at a glance

```
 (0) INGEST          (1) MAP            (2) BUILD           (3) VALIDATE        (4) UPLOAD          (5) EXPORT
 local file / URI -> extract & map  ->  compact instance -> validate against -> POST to CEDAR   -> write JSON + YAML
 -> raw metadata     to Canopy fields   YAML (+ render      the template         (needs API key)    for Canopy
                     (flag gaps)         to CEDAR JSON)
```

Stages 3–4 are where CEDAR's quirks bite. Section 5 is a field cheat-sheet; Section 6 is the troubleshooting that makes uploads succeed on the first try.

---

## 3. The prompts (run in order)

### Stage 0 — Ingest the source metadata

**If the source is a URI:**
```
Fetch the study metadata at <URI>.
- Prefer a structured/JSON representation over rendered HTML. If the landing page is
  an HTML/JS app, look for its API/JSON endpoint (e.g. a repository record API) or the
  DataCite record for the DOI (https://api.datacite.org/dois/<DOI>) to get authoritative
  fields like the full author/creator list, dates, sizes, and license.
- If the fetch response is too large to read at once, save it and extract only the
  fields I ask for in Stage 1 (title, description, contacts, authors, dates, keywords,
  access/rights, data types, sizes, related identifiers).
Summarize the fields you found; do not build anything yet.
```

**If the source is a local file (CSV, XLSX, PDF, README, protocol, data dictionary):**
```
Read the file(s) at <path>. Extract the study-level metadata: title, description/abstract,
PI/contact and submitter, authors, funding, dates (start/end/issued), access level/license,
study design, population, sample types, data types, measurement techniques, and keywords.
List what you found and, explicitly, what is missing. Do not build anything yet.
```

> **Tip:** DataCite (`https://api.datacite.org/dois/<DOI>`) is the most reliable source
> for the complete author list and ORCIDs when a repository landing page only shows a contact.

### Stage 1 — Map to Canopy fields (and flag gaps)

```
Map the extracted metadata onto the Canopy Study Metadata template
(https://repo.metadatacenter.org/templates/aff00b59-0bb7-4e40-9437-3216e5fb0ff7),
using the field cheat-sheet I'm providing (Section 5 of the pipeline doc).

Rules:
- Fill every REQUIRED field. If a required value is genuinely absent from the source,
  use a clear placeholder ("Not specified" / "Not applicable (<reason>)") and list it
  under "Assumptions & gaps" at the end — never invent facts (no fake emails, DOIs, grant #s).
- For controlled checkbox/radio fields, choose ONLY from the allowed option labels.
- For dates with unknown values that are required, use the best available proxy
  (e.g. publication/issued date) and flag it.
Produce a plain-language mapping table first (field -> value -> source/assumption),
and wait for my OK before building.
```

### Stage 2 — Build the compact instance

```
Build the CEDAR instance as compact YAML, isBasedOn the Canopy template ID.
Follow the CEDAR value-shape rules (Section 6):
- text/textarea/email/radio/temporal: { value: ... }   (temporal also needs datatype: xsd:date)
- numeric: { value: <number> }
- checkbox (multi): a LIST of { value: <label> }; every checkbox needs >= 1 entry
- single-option checkbox that does NOT apply: [ { value: null } ]  (present-but-unselected)
- link / DOI / ORCID (as link) / ext-* : { id: <url> }
- multi-instance element (e.g. authors): a list of
    - type: element-instance
      children: { sub_field: { value/id: ... }, ... }
Show me the YAML.
```

### Stage 3 — Render to CEDAR JSON and validate

```
Because the Canopy template uses UUID-based property IRIs, do NOT rely on server-side
inflation of a sparse instance. Instead:
1. Call cedar-artifact render_instance_artifact with format=json, compact=false, passing
   BOTH my compact instance and the Canopy template, to produce a complete CEDAR JSON-LD
   instance with the correct @context property IRIs and value objects.
2. Report any issues. Fix value shapes and re-render until it's clean.
(If you have the template as YAML with the real propertyIri UUIDs, use that; otherwise
fetch it first with cedar-artifact-rest get_template.)
```

### Stage 4 — Upload to CEDAR

```
Upload the complete JSON instance to CEDAR with cedar-artifact-rest create_instance
(format: json). It will be placed in my CEDAR home folder and the server will assign the
real @id. If the server returns validation errors, apply the Section 6 fixes
(usually: a checkbox with 0 elements -> add >= 1 or [ {@value: null} ]; an empty single
link field -> omit that field entirely; numeric/temporal missing @type). Re-upload until
it succeeds, then report the new instance @id and its CEDAR URL.
```

### Stage 5 — Export for Canopy

```
Save the final instance to my outputs folder in BOTH forms:
- <study-slug>-canopy-instance.json  (the exact CEDAR JSON-LD that was accepted)
- <study-slug>-canopy-instance.yaml  (the compact human-readable form)
Then present both files. Also give me the CEDAR instance URL and a one-paragraph summary
of any placeholder/assumed fields I should review before using it in Canopy.
```

---

## 4. Verification step (recommended)

```
Validate the uploaded instance independently: fetch it back with
cedar-artifact-rest get_instance and confirm (a) isBasedOn is the Canopy template,
(b) all required fields are non-empty, (c) the author/contact info matches the source.
Report a short pass/fail checklist.
```

---

## 5. Canopy field cheat-sheet

Template: **Canopy Study Metadata Specification v2** (`aff00b59-0bb7-4e40-9437-3216e5fb0ff7`).

**Required fields (must have a value):**
Center · Study Name · Access Level · PI Name · PI Email · PI Institution ·
Data Submitter Name · Data Submitter Email · Grant or Contract Number(s) ·
NIH Program Officer · FOA Number · Study Start Date · Study End Date · Study Domain ·
Data Collection Methods · Study Population Focus · Acknowledgment Statement · Study Description.

**Radio (choose exactly one):**
- Access Level: `Public` | `Limited Access` | `Private`

**Checkbox fields — IMPORTANT: each requires at least one selection** (see §6):
Required Documents · Is it a Multi-Center Study? · Data Availability · NIH Institute / Center ·
Study Domain · Data Collection Methods · Study Population Focus · Study Design · Species ·
Sample Collection · Data Types · Genomic Data Types · Phenotypes · Sample Types · Genotypes ·
Sequencing Data Types · Genomic Analyses Types · Genomic Array Data Types ·
General Research Use · Health/Medical/Biomedical · Conditions/Diseases.

**Free text / other:**
- Text: Center, Study Name, PI/Submitter names & institution, Related Conditions,
  "If multi-center study, list study sites", the various "Other ..." companion fields.
- Email: PI Email, Data Submitter Email.
- Temporal (date): Submission Date, Target Data Delivery Date, Study Start/End Date.
- Numeric: Estimated Number of Study Participants (decimal), Estimated Study Data Size (GB) (double).
- Link (URL): Clinical Trials gov URL, Study Website URL, Primary Publication URL.
- Text area: Acknowledgment Statement, Study Description.

**Sensible defaults when the field doesn't fit a non-COVID / non-NIH study:**
- NIH Program Officer / Grant / FOA → `Not applicable (<reason>)`.
- NIH Institute / Center → pick the topically closest IC and flag it (there is no "N/A" option).
- Data-use-limitation checkboxes (General Research Use, etc.) → for fully open data there is no
  "no limitations" option; pick the mildest and flag it.
- Multi-Center = No → represent "Is it a Multi-Center Study?" as `[ { value: null } ]`.

---

## 6. CEDAR gotchas & fixes (the part that saves you)

These are the concrete failures seen with this template and how to resolve them.

1. **Every checkbox requires ≥ 1 element.** A checkbox left empty (`[]`) fails with
   *"array is too short: must have at least 1 elements"*. Options:
   - It applies → list the real selections: `[{ value: "Human" }]`.
   - It genuinely doesn't apply but is a single-option box (e.g. Multi-Center) →
     use present-but-unselected: `[{ value: null }]`.
   - Irrelevant genomics boxes on a non-genomic study → select `Other` and add a note in the
     matching "Other ..." text field (e.g. "Not applicable — no genomic data").

2. **`@context` must use the template's UUID property IRIs.** If you upload a sparse compact
   instance, the server may generate generic `.../properties/<FieldName>` IRIs that don't match
   the template's enum, causing many *"not found in enum"* errors. **Fix:** render to full JSON
   locally with `render_instance_artifact` (passing the template) and upload that JSON.

3. **Empty single-instance link fields.** Sending `{}` or `{ "@id": null }` for an unused link
   field triggers *"properties which are not allowed: ['@value']"*. **Fix:** omit that field
   entirely from your instance — the server materializes it as blank. (This works for links;
   it does NOT work for checkboxes, which must be present with ≥ 1 element.)

4. **Numeric & temporal need `@type`.** Emit `{ "@value": "2024-12-06", "@type": "xsd:date" }`
   and `{ "@value": "40", "@type": "xsd:decimal" }`. The local render step adds these for you.

5. **Multi-instance elements (authors).** In compact YAML each entry is:
   ```yaml
   authors:
     - type: element-instance
       children:
         author_name: { value: "Jane Doe" }
         author_orcid: { id: https://orcid.org/0000-0002-1825-0097 }
         author_affiliation: { value: "NIST" }
   ```
   `minItems: 0` means the editor opens with no author card shown — that's a UI effect, the
   element is still repeatable. Set `minItems: 1` on the template if you want a card by default.

6. **Never fabricate.** Missing required values get honest placeholders and a flagged
   "Assumptions & gaps" list, not invented DOIs, emails, or grant numbers.

7. **Large fetches.** If a URI response exceeds the read limit, save it and extract only the
   needed fields (grep/jq), or use the DOI's DataCite record for the clean structured version.

---

## 7. One-shot driver prompt (paste-and-go)

```
You are running the "Canopy Study Metadata Pipeline". Target template:
https://repo.metadatacenter.org/templates/aff00b59-0bb7-4e40-9437-3216e5fb0ff7

Source: <LOCAL PATH or URI or DOI>

Do this end to end, pausing after the mapping table for my approval:
1. INGEST: fetch/read the source; prefer structured JSON (repository API or
   https://api.datacite.org/dois/<DOI>) over rendered HTML. Get the FULL author list.
2. MAP: produce a field -> value -> source/assumption table against the Canopy template.
   Fill all required fields; use clear placeholders for genuinely-missing values and list
   them under "Assumptions & gaps". Never invent facts. [WAIT FOR MY OK]
3. BUILD: compact YAML instance, isBasedOn the template. Follow CEDAR value shapes:
   text/email/radio/temporal={value}; temporal+numeric include datatype; checkboxes are
   lists with >=1 entry (use [{value:null}] for an unselected single-option box); links/DOIs
   /ORCIDs-as-links={id:url}; authors as element-instances.
4. RENDER+VALIDATE: cedar-artifact render_instance_artifact (format=json, with the template)
   to get complete CEDAR JSON-LD with correct @context; fix shapes until clean.
5. UPLOAD: cedar-artifact-rest create_instance (format:json). On errors apply fixes:
   empty checkbox -> add >=1 or [{@value:null}]; empty single link -> omit the field;
   numeric/temporal -> ensure @type. Report the new instance @id + CEDAR URL.
6. EXPORT: save <slug>-canopy-instance.json and .yaml to my outputs folder, present both,
   and summarize the assumed/placeholder fields I should review before loading into Canopy.

Prerequisite: the cedar-artifact-rest server must have my CEDAR API key configured; ping it first.
```

---

## 8. Adapting the pipeline

- **Different template?** Swap the template ID everywhere and regenerate the §5 cheat-sheet by
  fetching the template (`get_template`) and listing its required fields + checkbox options.
- **Add ontology-bound fields?** Insert a step that calls `bioportal-term` to resolve terms
  (class or branch IRIs) before build, and use `{ id: <iri>, label: <term> }` values.
- **Batch mode?** Loop stages 0–5 over a list of DOIs/files; keep one export file per study.
```
