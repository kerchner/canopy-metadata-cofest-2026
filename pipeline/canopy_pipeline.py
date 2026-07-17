#!/usr/bin/env python3
"""
canopy_pipeline.py — deterministic helper for the Canopy Study Metadata pipeline.

Handles the mechanical steps of the pipeline described in
`canopy-study-metadata-pipeline.md`:

  fetch    Pull structured metadata for a DOI/URI and emit a pre-filled mapping skeleton.
  build    Turn an approved field->value mapping (YAML) into valid CEDAR JSON-LD,
           pre-validate it, and write <slug>-canopy-instance.json + .yaml.
           Add --upload to POST it to the CEDAR server (needs an API key).

The field->propertyIRI map for the Canopy Study Metadata template
(aff00b59-0bb7-4e40-9437-3216e5fb0ff7) is baked in, so the JSON-LD @context is correct
without any server round-trip. The LLM/human still does the *semantic* mapping
(Stage 1 of the playbook); this script does the deterministic build/validate/upload/export.

Dependencies:  pip install pyyaml requests
  (requests is only needed for --upload / fetch; build works with stdlib + pyyaml.)

Environment for --upload:
  CEDAR_API_KEY     your CEDAR API key (Profile page at https://cedar.metadatacenter.org)
  CEDAR_FOLDER_ID   target folder @id, e.g. https://repo.metadatacenter.org/folders/<uuid>
                    (open your home folder in the CEDAR workbench; the UUID is in the URL)
  CEDAR_BASE        optional, default https://resource.metadatacenter.org
"""
from __future__ import annotations
import argparse, json, os, re, sys, urllib.parse, urllib.request
from collections import OrderedDict

try:
    import yaml
except ImportError:
    sys.exit("Missing dependency: pip install pyyaml")

TEMPLATE_ID = "https://repo.metadatacenter.org/templates/aff00b59-0bb7-4e40-9437-3216e5fb0ff7"
PROP = "https://schema.metadatacenter.org/properties/"

# ---------------------------------------------------------------------------
# Canopy Study Metadata template field registry.
#   kind: text | textarea | email | radio | date | numeric | link | checkbox
#   req:  required field
#   multi: repeatable (list) — applies to text/link
#   dt:   xsd datatype for numeric fields
# Static section-break fields are intentionally omitted (they hold no instance data).
# ---------------------------------------------------------------------------
F = OrderedDict()
def _f(name, uuid, kind, req=False, multi=False, dt=None):
    F[name] = {"iri": PROP + uuid, "kind": kind, "req": req, "multi": multi, "dt": dt}

_f("Center", "e3d2b1fb-6f2b-4e17-9e7e-8e9614b98263", "text", req=True)
_f("Study Name", "a90fb6b4-d918-484c-a9e0-03dfef7ff677", "text", req=True)
_f("Access Level", "74f573ec-854b-47a4-b204-5129ec11fa0c", "radio", req=True)
_f("Required Documents", "1a07902a-b6e9-4e47-9774-7bdd0a2bd105", "checkbox")
_f("Estimated Number of Study Participants", "26faf3ad-de12-4311-b8fc-890114a6352d", "numeric", dt="xsd:decimal")
_f("Is it a Multi-Center Study?", "afb42b1d-1475-4680-92e8-ebb5a483f07a", "checkbox")
_f("If multi-center study, list study sites", "68fcff67-a4ef-4618-91ab-21b7ee3eb14b", "text")
_f("Data Availability", "fe87e2ca-69e2-4fb6-bbcb-59e8c1465c5a", "checkbox")
_f("Other Data Availability", "a9ce74e1-daab-431c-b616-7fa939ebd57f", "text", multi=True)
_f("Submission Date", "61a727ed-8815-43a9-aab0-aaa848a3f555", "date")
_f("Data submission timeline details", "4c3c2652-8ef0-4da9-a42a-94c8db04b741", "text")
_f("Target Data Delivery Date", "dd766e19-fea8-4a3f-8370-6d90d37beac2", "date")
_f("Estimated Study Data Size (GB)", "efc794d7-c8eb-4f6e-84a9-9a10d2751926", "numeric", dt="xsd:double")
_f("PI Name", "37fd24c7-2a57-47a8-8d87-76f772bdb305", "text", req=True)
_f("PI Email", "f0e12b0a-273d-45ea-b27f-d21aa0eb5e6d", "email", req=True)
_f("PI Institution", "93495749-f8be-43f8-9afb-8fe408e3af0d", "text", req=True)
_f("Data Submitter Name", "1c8375c5-c43d-45e2-811b-e3b650370e10", "text", req=True)
_f("Data Submitter Email", "2b8f1259-6a2c-4868-ae15-7b9de2b5bcb6", "email", req=True)
_f("Grant or Contract Number(s)", "b378d7b1-cba2-472a-afbf-4798eab7955c", "text", req=True, multi=True)
_f("NIH Program Officer", "49fd8238-99e4-4f90-aa22-709c0d8beaae", "text", req=True)
_f("NIH Institute / Center", "ff30e315-579e-4610-a538-3af316fc3726", "checkbox")
_f("FOA Number", "81bfe156-5f42-4e6d-ab67-c445265b32bc", "text", req=True, multi=True)
_f("Study Start Date", "9dc64bbd-0ff5-4d4a-ab03-13ff469401bc", "date", req=True)
_f("Study End Date", "8558c8a5-c090-475f-9ec4-bc0b89edd8c9", "date", req=True)
_f("Study Domain", "3cc14e65-a37d-49c8-a964-c9885cbb3361", "checkbox", req=True)
_f("Other Domain, Specify", "33ba2e24-e763-4ae0-a2b4-1a135408a1c5", "text", multi=True)
_f("Data Collection Methods", "77e9b58d-8119-41e7-b77a-1f997af7d4c1", "checkbox", req=True)
_f("Other Data Collection Methods", "532392d2-badf-44b4-8bf6-8e14279a6c14", "text", multi=True)
_f("Study Population Focus", "6b45b13c-4709-4964-8dfc-ad28def3bd8d", "checkbox", req=True)
_f("Clinical Trials gov URL", "496c3d24-e5fd-4bd4-9980-d4e7d27c141c", "link")
_f("Study Website URL", "68fc4aaf-60f5-417c-997b-bdf8e305653e", "link")
_f("Primary Publication URL", "323a9da5-33aa-4c63-b053-3aa01af7b92e", "link", multi=True)
_f("Study Design", "b368c75f-fbf1-46c4-b161-00575b1b6ee5", "checkbox")
_f("Other Study Design", "8fbd5a7e-95aa-4ce4-a357-12f2d6d9fcae", "text", multi=True)
_f("Species", "1c72fe29-b869-4be6-9257-60cd537e387e", "checkbox")
_f("Sample Collection", "ea6f3dac-39b5-47f2-92a3-35f31152c4cd", "checkbox")
_f("Data Types", "908c2caa-e3a7-4a54-abb2-04a6f9ff0f4c", "checkbox")
_f("Other Data Types", "37c3750f-6591-4212-8505-5c7f048c3c11", "text", multi=True)
_f("Genomic Data Types", "e64a5dec-ad7e-466d-a466-bdf91deddd07", "checkbox")
_f("Other Genomic Data Types", "c9f74603-a09c-4dfb-a1e5-4f8daa93a2c1", "text", multi=True)
_f("Phenotypes", "bb3aba06-e07d-4471-82ac-ef62249ac5f8", "checkbox")
_f("Other Phenotypes", "c9e28656-dd2e-482b-8bb5-eda44c41c79e", "text", multi=True)
_f("Sample Types", "0590face-9f5c-4ac5-bbee-06ec11e664a7", "checkbox")
_f("Other Sample Types", "c2148c72-1281-4d03-9767-d87ab2edcfbf", "text", multi=True)
_f("Genotypes", "12692abb-4426-464f-814d-24ade580d92b", "checkbox")
_f("Other Genotypes", "a3dfaee6-1b21-4c27-bb81-b917f859f610", "text", multi=True)
_f("Sequencing Data Types", "ecb68cb5-ea2a-48b7-8b34-b5a6c160d3d2", "checkbox")
_f("Other Sequencing Data Types", "a86f7e7a-ca95-450e-bad1-fb549173d9ef", "text", multi=True)
_f("Genomic Analyses Types", "d4cd81b0-e57c-4dce-8e93-f9ab882985b5", "checkbox")
_f("Other Genomic Analyses Types", "8c75dd80-e9d5-4b56-8f22-831d28e4ed91", "text", multi=True)
_f("Genomic Array Data Types", "ac474736-d2c9-4396-b3eb-7d78dfcf1973", "checkbox")
_f("Other Genomic Array Data Types", "040f7afe-6eb0-4c46-81d4-d698456ead0f", "text", multi=True)
_f("Acknowledgment Statement", "55de1f80-766a-418a-ae55-92138743c84a", "textarea", req=True)
_f("Study Description", "f4c06fc8-eb0d-411b-88bf-5116cbb3e395", "textarea", req=True)
_f("General Research Use", "01e842ea-515d-4dda-acbe-80ff97b81072", "checkbox")
_f("Health/Medical/Biomedical", "1c0842fb-dfef-4b75-b5c6-cb86afdf4bba", "checkbox")
_f("Conditions/Diseases", "81328fdb-6db1-4e91-bf9f-c21f1ef9b23c", "checkbox")
_f("Related Conditions", "8ccf6dbe-c3ea-4d13-9f36-3052faf99743", "text")
_f("Other Data Use Limitations", "eaae0f3a-426c-4d46-bd83-01d204549415", "text")

CTX_BASE = OrderedDict([
    ("rdfs", "http://www.w3.org/2000/01/rdf-schema#"),
    ("xsd", "http://www.w3.org/2001/XMLSchema#"),
    ("pav", "http://purl.org/pav/"),
    ("schema", "http://schema.org/"),
    ("oslc", "http://open-services.net/ns/core#"),
    ("skos", "http://www.w3.org/2004/02/skos/core#"),
    ("rdfs:label", {"@type": "xsd:string"}),
    ("schema:isBasedOn", {"@type": "@id"}),
    ("schema:name", {"@type": "xsd:string"}),
    ("schema:description", {"@type": "xsd:string"}),
    ("pav:derivedFrom", {"@type": "@id"}),
    ("pav:createdOn", {"@type": "xsd:dateTime"}),
    ("pav:createdBy", {"@type": "@id"}),
    ("pav:lastUpdatedOn", {"@type": "xsd:dateTime"}),
    ("oslc:modifiedBy", {"@type": "@id"}),
    ("skos:notation", {"@type": "xsd:string"}),
])


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def _as_list(v):
    return v if isinstance(v, list) else [v]


def build_instance(mapping: dict, name: str):
    """Turn a friendly field->value mapping into CEDAR JSON-LD. Returns (instance, warnings)."""
    warnings, problems = [], []
    unknown = [k for k in mapping if k not in F and k not in ("_name", "_slug")]
    if unknown:
        warnings.append("Ignoring unknown field(s): " + ", ".join(unknown))

    inst = OrderedDict()
    inst["schema:name"] = name
    ctx = OrderedDict(CTX_BASE)

    for fname, spec in F.items():
        kind, val = spec["kind"], mapping.get(fname, None)
        has = val not in (None, "", [])

        # empty single-instance link fields must be OMITTED (CEDAR rejects empty {})
        if kind == "link" and not spec["multi"] and not has:
            continue

        ctx[fname] = spec["iri"]

        if kind in ("text", "textarea", "email"):
            if spec["multi"]:
                inst[fname] = [{"@value": str(x)} for x in _as_list(val)] if has else []
            else:
                inst[fname] = {"@value": (str(val) if has else None)}
        elif kind == "radio":
            inst[fname] = {"@value": (str(val) if has else None)}
        elif kind == "date":
            inst[fname] = {"@value": (str(val) if has else None), "@type": "xsd:date"}
        elif kind == "numeric":
            inst[fname] = {"@value": (str(val) if has else None), "@type": spec["dt"]}
        elif kind == "link":
            if spec["multi"]:
                inst[fname] = [{"@id": str(x)} for x in _as_list(val)] if has else []
            else:
                inst[fname] = {"@id": str(val)}  # single; empty case already omitted above
        elif kind == "checkbox":
            # Every checkbox needs >= 1 element. Unselected -> present-but-null.
            inst[fname] = [{"@value": str(x)} for x in _as_list(val)] if has else [{"@value": None}]

        if spec["req"] and not has:
            problems.append(fname)

    ctx.update({k: v for k, v in CTX_BASE.items() if k not in ctx})  # keep base keys first anyway
    inst["@context"] = ctx
    inst["schema:isBasedOn"] = TEMPLATE_ID
    inst["schema:description"] = ""
    return inst, warnings, problems


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------
def upload(instance: dict):
    key = os.environ.get("CEDAR_API_KEY")
    folder = os.environ.get("CEDAR_FOLDER_ID")
    base = os.environ.get("CEDAR_BASE", "https://resource.metadatacenter.org")
    if not key or not folder:
        sys.exit("Upload needs CEDAR_API_KEY and CEDAR_FOLDER_ID environment variables.")
    url = f"{base}/template-instances?folder_id=" + urllib.parse.quote(folder, safe="")
    body = json.dumps(instance).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Authorization": "apiKey " + key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req) as r:
            created = json.load(r)
        iid = created.get("@id", "(unknown)")
        print(f"  uploaded: {iid}")
        return iid
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        print(f"  CEDAR HTTP {e.code}:\n{detail}", file=sys.stderr)
        raise SystemExit("Upload failed — see CEDAR validation report above.")


# ---------------------------------------------------------------------------
# Fetch (DataCite for DOIs; raw JSON for other URIs) -> mapping skeleton
# ---------------------------------------------------------------------------
def _get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json",
                                               "User-Agent": "canopy-pipeline/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch_skeleton(source: str) -> dict:
    doi = None
    m = re.search(r"10\.\d{4,9}/[^\s\"'>]+", source)
    if m:
        doi = m.group(0).rstrip(".")
    mp = OrderedDict()
    if doi:
        d = _get("https://api.datacite.org/dois/" + urllib.parse.quote(doi, safe=""))
        a = d["data"]["attributes"]
        mp["Study Name"] = (a.get("titles") or [{}])[0].get("title", "")
        descs = a.get("descriptions") or []
        mp["Study Description"] = descs[0]["description"] if descs else "TODO: abstract"
        mp["Center"] = a.get("publisher", "")
        mp["Access Level"] = "Public"
        contact = next((c["name"] for c in a.get("contributors", [])
                        if c.get("contributorType") == "ContactPerson"), "")
        mp["PI Name"] = contact or "TODO"
        mp["PI Email"] = "TODO: contact email"
        mp["PI Institution"] = a.get("publisher", "")
        mp["Data Submitter Name"] = contact or "TODO"
        mp["Data Submitter Email"] = "TODO: submitter email"
        mp["Study Website URL"] = a.get("url", "")
        if a.get("publicationYear"):
            mp["Submission Date"] = f"{a['publicationYear']}-01-01  # TODO verify"
        creators = [c.get("name", "") for c in a.get("creators", [])]
        if creators:
            mp["_creators_note"] = ("Canopy has no author field; DataCite creators = "
                                    + "; ".join(creators))
        print(f"# Source: DataCite DOI {doi}", file=sys.stderr)
    else:
        try:
            raw = _get(source)
            print("# Fetched JSON; inspect and map fields manually.", file=sys.stderr)
            print(json.dumps(raw, indent=2)[:4000], file=sys.stderr)
        except Exception as e:
            print(f"# Could not fetch {source} as JSON: {e}", file=sys.stderr)
        mp["Study Name"] = "TODO"
    # required fields the LLM/user must complete
    for req in [n for n, s in F.items() if s["req"] and n not in mp]:
        mp[req] = "TODO"
    mp["_name"] = mp.get("Study Name", "study") + " — Canopy study metadata"
    mp["_slug"] = re.sub(r"[^a-z0-9]+", "-", (doi or "study").lower()).strip("-")
    return mp


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def cmd_fetch(args):
    mp = fetch_skeleton(args.source)
    out = yaml.safe_dump(dict(mp), sort_keys=False, allow_unicode=True)
    if args.out:
        open(args.out, "w").write(out)
        print(f"Wrote mapping skeleton: {args.out}  (fill in the TODOs, then run 'build')")
    else:
        print(out)


def cmd_build(args):
    mapping = yaml.safe_load(open(args.mapping))
    if not isinstance(mapping, dict):
        sys.exit("Mapping file must be a YAML dict of field -> value.")
    name = mapping.get("_name") or (mapping.get("Study Name", "study") + " — Canopy study metadata")
    slug = mapping.get("_slug") or re.sub(r"[^a-z0-9]+", "-", str(mapping.get("Study Name", "study")).lower()).strip("-")[:60]

    inst, warnings, problems = build_instance(mapping, name)
    for w in warnings:
        print("  warning:", w)
    if problems and not args.allow_missing:
        print("  MISSING required fields:", ", ".join(problems), file=sys.stderr)
        sys.exit("Fill the required fields (or pass --allow-missing to write anyway with nulls).")

    plain = json.loads(json.dumps(inst))  # OrderedDict -> plain dict (order preserved)
    json_path = f"{slug}-canopy-instance.json"
    yaml_path = f"{slug}-canopy-instance.yaml"
    json.dump(plain, open(json_path, "w"), indent=2, ensure_ascii=False)
    yaml.safe_dump(plain, open(yaml_path, "w"), sort_keys=False, allow_unicode=True)
    print(f"  wrote {json_path}")
    print(f"  wrote {yaml_path}")

    if args.upload:
        upload(inst)
    else:
        print("  (skipped upload; pass --upload to POST to CEDAR)")


def main():
    p = argparse.ArgumentParser(description="Canopy Study Metadata pipeline helper.")
    sub = p.add_subparsers(dest="cmd", required=True)

    pf = sub.add_parser("fetch", help="Fetch metadata for a DOI/URI -> mapping skeleton.")
    pf.add_argument("source", help="DOI, DOI URL, or a JSON metadata URL.")
    pf.add_argument("-o", "--out", help="Write skeleton YAML here (default: stdout).")
    pf.set_defaults(func=cmd_fetch)

    pb = sub.add_parser("build", help="Build/validate/export (and optionally upload) an instance.")
    pb.add_argument("mapping", help="YAML mapping file (field -> value).")
    pb.add_argument("--upload", action="store_true", help="POST to CEDAR (needs API key env vars).")
    pb.add_argument("--allow-missing", action="store_true", help="Write even if required fields are blank.")
    pb.set_defaults(func=cmd_build)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
