# Synthetic study — SPbE-2026

> **Effect of 12-Week Time-Restricted Eating on Glycemic Control in Prediabetic Adults: A Synthetic Pilot Study.**

Everything here is **AI-generated and entirely fictional** — no real subjects, no real results. It exists so anyone can run the AI-assisted metadata pipeline end-to-end without sensitive data.

| File | What it is | Plays the role of |
|---|---|---|
| `SPbE-2026_dataset.xlsx` | 40 subjects × 20 columns of measurements, plus a `data_dictionary` sheet (column → description, type, units, ontology term). | the researcher's **dataset** |
| `SPbE-2026_protocol.pdf` | Study protocol: background, objectives, design, eligibility, measurements, analysis. | the **protocol / paper** |
| `SPbE-2026_SOP_sample-collection.pdf` | SOP for blood sample collection & handling. | a supplementary **SOP** |

These are the Step 0 inputs. The pipeline reads them and infers metadata for both the Canopy Study template (Step 2) and the domain-specific template (Step 3).

Regenerate with `python3 ../../src/gen_data.py` (seed-fixed, reproducible).
