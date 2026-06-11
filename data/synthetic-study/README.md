# Synthetic study — SPbE-2026

> **Effect of 12-Week Time-Restricted Eating on Glycemic Control in Prediabetic Adults: A Synthetic Pilot Study.**

Everything here is **AI-generated and entirely fictional** — no real subjects, no real results. It exists so anyone can run the AI-assisted metadata workflow end-to-end without sensitive data.

| File | What it is | Plays the role of |
|---|---|---|
| `SPbE-2026_dataset.xlsx` | 40 subjects × 20 columns of measurements, plus a `data_dictionary` sheet (column → type, authority, units, example, ontology term). | the researcher's **dataset** |
| `SPbE-2026_dataset.csv` | The same measurements in CSV (open format, no licensing concerns). | the **dataset**, plain-text form |
| `SPbE-2026_protocol.pdf` | ~10-page study protocol: synopsis, background, objectives, design, eligibility, procedures, measurements, analysis, governance, glossary, and a data-dictionary appendix. | the **protocol / paper** |
| `SPbE-2026_SOP_sample-collection.pdf` | SOP for blood sample collection & handling. | a supplementary **SOP** |

The 20 columns deliberately span varied CEDAR field types — numeric, date, boolean, ontology-controlled (`sex`, `country`, `condition`, `study_arm`), and external identifiers (`investigator_orcid`, `reference_pmid`, `protocol_doi`) — so the example exercises real metadata, not 20 strings. See the structure table in the [main README](../../README.md#what-we-provide-example-input-data).

These are the Step 0 inputs — **one example**; the approach must handle any such artifacts. The workflow reads them to fill the Canopy Study template (Step 1) and to create and fill a domain-specific template (Steps 2–3).

Regenerate with `python3 ../../src/gen_data.py` (seed-fixed, reproducible).
