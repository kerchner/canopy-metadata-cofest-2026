#!/usr/bin/env python3
"""Generate a synthetic study (SPbE-2026) for the Canopy AI metadata CoFest demo.
All data is fictional. No real subjects."""
import random
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, ListFlowable, ListItem)

random.seed(42)
OUT = Path("/sessions/sharp-intelligent-mendel/mnt/CANOPY_PROD/canopy-metadata-cofest-2026/data/synthetic-study")
OUT.mkdir(parents=True, exist_ok=True)

STUDY_ID = "SPbE-2026"
STUDY_TITLE = ("Effect of 12-Week Time-Restricted Eating on Glycemic Control "
               "in Prediabetic Adults: A Synthetic Pilot Study")

# ---------------------------------------------------------------- spreadsheet
COLUMNS = [
    ("subject_id",            "Subject identifier"),
    ("age_years",             "Age at enrollment"),
    ("sex",                   "Biological sex"),
    ("group",                 "Study arm"),
    ("bmi_kg_m2",             "Body mass index"),
    ("baseline_glucose_mg_dl","Fasting plasma glucose, baseline"),
    ("week12_glucose_mg_dl",  "Fasting plasma glucose, week 12"),
    ("baseline_hba1c_pct",    "HbA1c, baseline"),
    ("week12_hba1c_pct",      "HbA1c, week 12"),
    ("baseline_weight_kg",    "Body weight, baseline"),
    ("week12_weight_kg",      "Body weight, week 12"),
    ("systolic_bp_mmhg",      "Systolic blood pressure, week 12"),
    ("diastolic_bp_mmhg",     "Diastolic blood pressure, week 12"),
    ("ldl_mg_dl",             "LDL cholesterol, week 12"),
    ("hdl_mg_dl",             "HDL cholesterol, week 12"),
    ("triglycerides_mg_dl",   "Triglycerides, week 12"),
    ("adherence_pct",         "Protocol adherence"),
    ("adverse_event",         "Any adverse event reported"),
    ("withdrew",              "Withdrew before week 12"),
    ("collection_date",       "Final visit date"),
]

def make_subject(i):
    grp = "TRE" if i % 2 == 0 else "control"
    age = random.randint(40, 65)
    sex = random.choice(["female", "male"])
    bmi = round(random.uniform(26.0, 34.0), 1)
    bg = random.randint(102, 124)               # prediabetic fasting glucose
    # TRE arm improves a bit more
    drop = random.randint(6, 16) if grp == "TRE" else random.randint(-2, 6)
    wg = max(88, bg - drop)
    b_a1c = round(random.uniform(5.7, 6.4), 1)
    a1c_drop = round(random.uniform(0.1, 0.5), 1) if grp == "TRE" else round(random.uniform(-0.1, 0.2), 1)
    w_a1c = round(max(5.2, b_a1c - a1c_drop), 1)
    b_wt = round(random.uniform(72, 102), 1)
    wt_drop = round(random.uniform(1.5, 5.5), 1) if grp == "TRE" else round(random.uniform(-1.0, 2.0), 1)
    w_wt = round(b_wt - wt_drop, 1)
    withdrew = random.random() < 0.07
    return [
        f"SUBJ-{i:03d}", age, sex, grp, bmi, bg,
        (None if withdrew else wg), b_a1c, (None if withdrew else w_a1c),
        b_wt, (None if withdrew else w_wt),
        random.randint(112, 138), random.randint(70, 88),
        random.randint(90, 150), random.randint(38, 60),
        random.randint(90, 210), random.randint(58, 99),
        random.choice(["no", "no", "no", "yes"]),
        ("yes" if withdrew else "no"),
        f"2026-0{random.randint(1,4)}-{random.randint(10,28):02d}",
    ]

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "measurements"
hdr_fill = PatternFill("solid", fgColor="1F6F54")
hdr_font = Font(bold=True, color="FFFFFF")
for c, (name, _) in enumerate(COLUMNS, 1):
    cell = ws.cell(1, c, name)
    cell.fill = hdr_fill; cell.font = hdr_font
    cell.alignment = Alignment(horizontal="center")
for r in range(2, 42):                          # 40 subjects
    for c, val in enumerate(make_subject(r - 1), 1):
        ws.cell(r, c, val)
ws.freeze_panes = "A2"
for col in ws.columns:
    width = max(len(str(x.value)) for x in col if x.value is not None) + 2
    ws.column_dimensions[col[0].column_letter].width = min(width, 22)

# data dictionary sheet
dd = wb.create_sheet("data_dictionary")
dd_headers = ["column_name", "description", "data_type", "units", "permissible_values", "ontology_reference"]
ONT = {
    "subject_id": ("string", "", "", ""),
    "age_years": ("integer", "years", "40-65", "NCIT:C25150 (Age)"),
    "sex": ("categorical", "", "female | male", "NCIT:C28421 (Sex)"),
    "group": ("categorical", "", "TRE | control", "NCIT:C15538 (Treatment Arm)"),
    "bmi_kg_m2": ("decimal", "kg/m^2", "", "NCIT:C16358 (Body Mass Index)"),
    "baseline_glucose_mg_dl": ("integer", "mg/dL", "", "NCIT:C105585 (Fasting Blood Glucose)"),
    "week12_glucose_mg_dl": ("integer", "mg/dL", "", "NCIT:C105585 (Fasting Blood Glucose)"),
    "baseline_hba1c_pct": ("decimal", "%", "", "NCIT:C64849 (Hemoglobin A1C)"),
    "week12_hba1c_pct": ("decimal", "%", "", "NCIT:C64849 (Hemoglobin A1C)"),
    "baseline_weight_kg": ("decimal", "kg", "", "NCIT:C25208 (Weight)"),
    "week12_weight_kg": ("decimal", "kg", "", "NCIT:C25208 (Weight)"),
    "systolic_bp_mmhg": ("integer", "mmHg", "", "NCIT:C25298 (Systolic Blood Pressure)"),
    "diastolic_bp_mmhg": ("integer", "mmHg", "", "NCIT:C25299 (Diastolic Blood Pressure)"),
    "ldl_mg_dl": ("integer", "mg/dL", "", "NCIT:C105586 (LDL Cholesterol)"),
    "hdl_mg_dl": ("integer", "mg/dL", "", "NCIT:C105587 (HDL Cholesterol)"),
    "triglycerides_mg_dl": ("integer", "mg/dL", "", "NCIT:C64812 (Triglycerides)"),
    "adherence_pct": ("integer", "%", "0-100", ""),
    "adverse_event": ("categorical", "", "yes | no", "NCIT:C41331 (Adverse Event)"),
    "withdrew": ("categorical", "", "yes | no", "NCIT:C49634 (Withdrawal)"),
    "collection_date": ("date", "ISO-8601", "", "NCIT:C81286 (Date)"),
}
for c, h in enumerate(dd_headers, 1):
    cell = dd.cell(1, c, h); cell.fill = hdr_fill; cell.font = hdr_font
for r, (name, desc) in enumerate(COLUMNS, 2):
    dt, units, pv, ont = ONT[name]
    for c, val in enumerate([name, desc, dt, units, pv, ont], 1):
        dd.cell(r, c, val)
for col in dd.columns:
    width = max(len(str(x.value)) for x in col if x.value is not None) + 2
    dd.column_dimensions[col[0].column_letter].width = min(width, 40)

xlsx_path = OUT / "SPbE-2026_dataset.xlsx"
wb.save(xlsx_path)
print("wrote", xlsx_path)

# ---------------------------------------------------------------- PDF helpers
styles = getSampleStyleSheet()
styles.add(ParagraphStyle("H", parent=styles["Heading1"], textColor=colors.HexColor("#1F6F54")))
styles.add(ParagraphStyle("H2b", parent=styles["Heading2"], textColor=colors.HexColor("#1F6F54")))
body = styles["BodyText"]; body.spaceAfter = 8

def build_pdf(path, flow):
    SimpleDocTemplate(str(path), pagesize=LETTER,
                      topMargin=0.9*inch, bottomMargin=0.9*inch,
                      leftMargin=1*inch, rightMargin=1*inch).build(flow)
    print("wrote", path)

def P(t, s="BodyText"): return Paragraph(t, styles[s])
def bullets(items): return ListFlowable([ListItem(P(i)) for i in items], bulletType="bullet", leftIndent=18)

# ---------------------------------------------------------------- protocol PDF
f = [
    P("Study Protocol", "H"),
    P(f"<b>{STUDY_TITLE}</b>"),
    P(f"Protocol ID: {STUDY_ID} &nbsp;|&nbsp; Version 1.0 &nbsp;|&nbsp; Synthetic / fictional data for software testing only."),
    Spacer(1, 10),
    P("1. Background and Rationale", "H2b"),
    P("Prediabetes affects a large fraction of middle-aged adults and is a major risk factor for "
      "progression to type 2 diabetes. Time-restricted eating (TRE), in which daily food intake is "
      "confined to a fixed window, has been proposed as a low-cost behavioral intervention to improve "
      "glycemic control. This synthetic pilot study models a randomized comparison of TRE versus an "
      "unrestricted-schedule control over 12 weeks. <i>All subjects and results in this protocol are "
      "fabricated for the purpose of testing AI-assisted metadata generation.</i>"),
    P("2. Objectives", "H2b"),
    P("Primary objective: estimate the effect of a 10-hour TRE window on change in fasting plasma "
      "glucose from baseline to week 12. Secondary objectives: change in HbA1c, body weight, blood "
      "pressure, and lipid panel; protocol adherence; and safety."),
    P("3. Study Design", "H2b"),
    bullets([
        "Design: two-arm, parallel-group, randomized pilot.",
        "Population: adults aged 40-65 with prediabetes (fasting glucose 100-125 mg/dL or HbA1c 5.7-6.4%).",
        "Arms: TRE (10-hour eating window, 08:00-18:00) vs. control (habitual eating schedule).",
        "Duration: 12 weeks. Visits at baseline and week 12.",
        "Target enrollment: 40 subjects (1:1 allocation).",
    ]),
    P("4. Eligibility", "H2b"),
    P("<b>Inclusion:</b> age 40-65; BMI 26-35 kg/m^2; documented prediabetes; able to provide informed "
      "consent. <b>Exclusion:</b> diagnosed diabetes; current use of glucose-lowering medication; "
      "pregnancy; active eating disorder; shift work preventing a fixed eating window."),
    P("5. Measurements", "H2b"),
    P("Fasting plasma glucose, HbA1c, body weight, BMI, systolic and diastolic blood pressure, and a "
      "fasting lipid panel (LDL, HDL, triglycerides) were recorded. Adherence was captured as the "
      "percentage of days the assigned eating window was followed, from participant diaries. All "
      "variables and their units are defined in the accompanying data dictionary."),
    P("6. Statistical Analysis", "H2b"),
    P("The primary endpoint (change in fasting glucose) will be compared between arms using a two-sample "
      "t-test, with a linear model adjusting for baseline value, age, and sex as a sensitivity analysis. "
      "Given the pilot sample size, results are intended to inform feasibility and effect-size estimates "
      "rather than confirmatory inference."),
    P("7. Ethics and Data Sharing", "H2b"),
    P("As a synthetic dataset, no human subjects were involved and no ethics approval applies. The data "
      "are released to support FAIR-metadata tooling and may be freely reused. Metadata for the study "
      "and its datasets are described using CEDAR templates and registered in the Canopy data hub."),
]
build_pdf(OUT / "SPbE-2026_protocol.pdf", f)

# ---------------------------------------------------------------- SOP PDF
f = [
    P("Standard Operating Procedure", "H"),
    P("<b>SOP: Fasting Plasma Glucose and HbA1c Sample Collection and Handling</b>"),
    P(f"SOP ID: {STUDY_ID}-SOP-001 &nbsp;|&nbsp; Version 1.0 &nbsp;|&nbsp; Synthetic example."),
    Spacer(1, 10),
    P("1. Purpose", "H2b"),
    P("To standardize the collection, labeling, processing, and storage of venous blood samples used to "
      "measure fasting plasma glucose and HbA1c, ensuring comparable results across visits and subjects."),
    P("2. Scope", "H2b"),
    P(f"Applies to all study staff collecting biospecimens for study {STUDY_ID} at baseline and week 12."),
    P("3. Materials", "H2b"),
    bullets([
        "Sodium fluoride / potassium oxalate tubes (grey-top) for glucose.",
        "EDTA tubes (lavender-top) for HbA1c.",
        "Pre-printed barcode labels linked to subject_id.",
        "Calibrated centrifuge, refrigerated transport box, validated -80 C freezer.",
    ]),
    P("4. Procedure", "H2b"),
    ListFlowable([ListItem(P(t)) for t in [
        "Confirm the participant has fasted >= 8 hours; record last food intake time.",
        "Collect blood by standard venipuncture into the grey-top tube first, then the lavender-top tube.",
        "Invert each tube gently 8-10 times immediately after collection. Do not shake.",
        "Label each tube with the barcode and record collection_date and time.",
        "Centrifuge the glucose tube within 30 minutes (1500 x g, 10 min, 4 C); separate plasma.",
        "Store HbA1c whole blood at 4 C and analyze within 72 hours; archive plasma aliquots at -80 C.",
        "Log every sample in the LIMS against the subject_id before end of day.",
    ]], bulletType="1", leftIndent=18),
    P("5. Quality Control", "H2b"),
    P("Run two levels of commercial control material with each analytical batch. Reject and recollect any "
      "sample with visible hemolysis or an unbroken cold chain. Document deviations on the deviation log."),
    P("6. Records", "H2b"),
    P("Retain collection logs, instrument calibration records, and QC results. These records map directly "
      "to the dataset fields collection_date, baseline_glucose_mg_dl, week12_glucose_mg_dl, "
      "baseline_hba1c_pct, and week12_hba1c_pct."),
]
build_pdf(OUT / "SPbE-2026_SOP_sample-collection.pdf", f)
print("DONE")
