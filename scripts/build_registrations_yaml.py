#!/usr/bin/env python3
"""
Build a HRA registrations YAML from a HuBMAP lung-blocks Excel spreadsheet.

For each row where Column B (millitome size) is non-empty:
  - Fetches the block entity from the HuBMAP Entity API
  - Walks UP the provenance chain to get donor info (age, sex, bmi)
  - Walks DOWN to get derived datasets and their assay technology
  - Loads the pre-built millitome RUI JSON from --rui-dir/{hubmap_id}.json
  - Writes one combined registrations.yaml grouped by donor

Usage:
    python build_registrations_yaml.py <excel_file> \\
        --token <hubmap_personal_token> \\
        [--rui-dir scripts/millitome_hubmap_jsons] \\
        [--output registrations.yaml] \\
        [--delay 0.6]
"""

import sys
import os
import re
import time
import argparse
import pandas as pd
import requests
import yaml

ENTITY_API  = "https://entity.api.hubmapconsortium.org"
PORTAL_BASE = "https://portal.hubmapconsortium.org/browse"
SCHEMA_URL  = ("https://raw.githubusercontent.com/hubmapconsortium/"
               "hra-rui-locations-processor/main/registrations.schema.json")

# ── Helpers ──────────────────────────────────────────────────────────────────

def extract_id(raw):
    """Return the bare HuBMAP ID / UUID from a cell that may be a portal URL."""
    s = str(raw).strip()
    if s.startswith("http"):
        return s.rstrip("/").split("/")[-1]
    return s


def api_get(session, url, delay):
    """GET with exponential back-off (3 attempts). Returns parsed JSON or None."""
    time.sleep(delay)
    for attempt in range(3):
        try:
            r = session.get(url, timeout=30)
            if r.status_code == 404:
                return None
            if r.status_code in (401, 403):
                print(f"\nFATAL: HTTP {r.status_code} — check your token.\n  URL: {url}")
                sys.exit(1)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as exc:
            if attempt == 2:
                print(f"  WARNING: 3 failed attempts — {url}\n    {exc}")
                return None
            time.sleep(1.5 * (attempt + 1))
    return None


def get_entity(session, id_, delay):
    return api_get(session, f"{ENTITY_API}/entities/{requests.utils.quote(id_)}", delay)


def get_ancestors(session, id_, delay):
    result = api_get(session, f"{ENTITY_API}/ancestors/{requests.utils.quote(id_)}", delay)
    return result if isinstance(result, list) else []


def get_descendants(session, id_, delay):
    result = api_get(session, f"{ENTITY_API}/descendants/{requests.utils.quote(id_)}", delay)
    return result if isinstance(result, list) else []


# ── Donor metadata extraction ─────────────────────────────────────────────────

def _organ_donor_items(donor):
    """Yield every dict inside metadata.organ_donor_data (if present)."""
    meta = donor.get("metadata") or {}
    items = meta.get("organ_donor_data") or []
    if isinstance(items, list):
        yield from items


def _find_donor_field(donor, *keywords):
    """
    Search organ_donor_data for a row whose grouping_concept_preferred_term
    matches any keyword (case-insensitive). Returns data_value or preferred_term.
    """
    for item in _organ_donor_items(donor):
        term = (item.get("grouping_concept_preferred_term") or "").lower()
        if any(kw.lower() in term for kw in keywords):
            return item.get("data_value") or item.get("preferred_term")
    return None


def extract_donor_info(donor):
    """Return a dict with sex, age (int), and bmi (float) where available."""
    if not donor:
        return {}

    info = {}

    # ── Sex ──────────────────────────────────────────────────────────────────
    # 1) top-level "sex" field (some donor entities have this)
    sex_raw = (donor.get("sex") or "").strip()
    # 2) fallback to organ_donor_data
    if not sex_raw:
        sex_raw = _find_donor_field(donor, "sex") or ""
    sex_map = {"male": "Male", "female": "Female", "m": "Male", "f": "Female"}
    mapped = sex_map.get(sex_raw.lower())
    if mapped:
        info["sex"] = mapped

    # ── Age ──────────────────────────────────────────────────────────────────
    age_raw = (donor.get("age_value") or
               donor.get("age") or
               _find_donor_field(donor, "age"))
    if age_raw is not None:
        try:
            info["age"] = int(float(age_raw))
        except (ValueError, TypeError):
            pass

    # ── BMI ──────────────────────────────────────────────────────────────────
    bmi_raw = (donor.get("bmi_value") or
               donor.get("bmi") or
               _find_donor_field(donor, "bmi", "body mass index"))
    if bmi_raw is not None:
        try:
            info["bmi"] = round(float(bmi_raw), 1)
        except (ValueError, TypeError):
            pass

    return info


# ── Dataset helpers ────────────────────────────────────────────────────────────

def extract_technology(ds):
    """Best-effort technology string from a dataset entity."""
    # data_types is a list in most HuBMAP dataset entities
    dt = ds.get("data_types")
    if isinstance(dt, list) and dt:
        return ", ".join(dt)
    if isinstance(dt, str) and dt:
        return dt
    # Newer HuBMAP API uses dataset_type
    for field in ("dataset_type", "assay_display_name", "assay_type"):
        val = ds.get(field)
        if val:
            return str(val)
    return "OTHER"


# ── RUI JSON loader ────────────────────────────────────────────────────────────

def load_rui(rui_dir, hubmap_id):
    """Return the JSON filename string if the file exists, else None."""
    path = os.path.join(rui_dir, f"{hubmap_id}.json")
    if not os.path.isfile(path):
        return None
    return f"{hubmap_id}.json"


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Build a HRA registrations YAML from HuBMAP lung-block data.")
    parser.add_argument("excel_file",
                        help="Path to the RUI hubmap blocks Excel spreadsheet")
    parser.add_argument("--token", required=True,
                        help="HuBMAP personal API token")
    parser.add_argument("--rui-dir", default="scripts/millitome_hubmap_jsons",
                        help="Directory of millitome JSON files "
                             "(default: scripts/millitome_hubmap_jsons)")
    parser.add_argument("--output", default="registrations.yaml",
                        help="Output YAML file path (default: registrations.yaml)")
    parser.add_argument("--delay", type=float, default=0.6,
                        help="Seconds to wait between API calls (default: 0.6)")
    args = parser.parse_args()

    # ── Validate inputs ───────────────────────────────────────────────────────
    if not os.path.isfile(args.excel_file):
        print(f"ERROR: Excel file not found: {args.excel_file}")
        sys.exit(1)
    if not os.path.isdir(args.rui_dir):
        print(f"ERROR: RUI directory not found: {args.rui_dir}")
        sys.exit(1)

    # ── HTTP session ──────────────────────────────────────────────────────────
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {args.token}",
        "Accept": "application/json",
    })

    # ── Read Excel ────────────────────────────────────────────────────────────
    df = pd.read_excel(args.excel_file, header=0)
    col_hubmap = df.columns[0]   # A — HuBMAP ID (may be hyperlink text)
    col_size   = df.columns[1]   # B — millitome size (skip row if empty)

    # Collect processable rows
    rows = []
    skipped = 0
    for idx, row in df.iterrows():
        if pd.isna(row[col_size]):
            skipped += 1
            continue
        rows.append((idx + 2, extract_id(row[col_hubmap])))

    print(f"Excel: {len(rows)} rows to process, {skipped} skipped (no millitome size).\n")

    # ── Fetch & assemble ──────────────────────────────────────────────────────
    # Keyed by donor UUID, preserving insertion order
    donors: dict[str, dict] = {}
    donor_order: list[str]  = []

    stats = {"ok": 0, "no_rui": 0, "no_donor": 0, "api_err": 0}
    total = len(rows)

    for i, (row_num, hubmap_id) in enumerate(rows, 1):
        print(f"[{i}/{total}] Row {row_num}: {hubmap_id}")

        # 1) RUI location JSON
        rui_location = load_rui(args.rui_dir, hubmap_id)
        if rui_location is None:
            print(f"  ⚠  No RUI JSON found at {args.rui_dir}/{hubmap_id}.json — skipping.")
            stats["no_rui"] += 1
            continue

        # 2) Block entity
        print(f"  → Fetching block entity…")
        block = get_entity(session, hubmap_id, args.delay)
        if not block:
            print(f"  ✗  Could not fetch block entity — skipping.")
            stats["api_err"] += 1
            continue

        block_uuid     = block.get("uuid", "")
        block_hubmap_id = block.get("hubmap_id", hubmap_id)
        block_label    = (block.get("lab_tissue_sample_id") or
                          block.get("lab_id") or
                          hubmap_id)
        # Strip leading D###- from lab ID (same logic as the previous script)
        block_label = re.sub(r'^D\d+-', '', str(block_label).strip())

        # 3) Ancestors → donor
        print(f"  → Fetching ancestors…")
        ancestors = get_ancestors(session, hubmap_id, args.delay)
        donor_entity = next(
            (a for a in ancestors if a.get("entity_type") == "Donor"), None)

        if not donor_entity:
            print(f"  ⚠  No Donor found in ancestors.")
            stats["no_donor"] += 1
            donor_uuid = f"UNKNOWN_{hubmap_id}"
            donor_info = {}
        else:
            donor_uuid = donor_entity.get("uuid", f"UNKNOWN_{hubmap_id}")
            donor_info = extract_donor_info(donor_entity)
            sex_display = donor_info.get("sex", "?")
            age_display = donor_info.get("age", "?")
            print(f"  ✓  Donor {donor_uuid[:8]}…  sex={sex_display}  age={age_display}")

        # 4) Descendants → datasets
        print(f"  → Fetching descendants…")
        descendants = get_descendants(session, hubmap_id, args.delay)
        datasets = [d for d in descendants if d.get("entity_type") == "Dataset"]
        print(f"  ✓  {len(datasets)} dataset(s) found.")

        dataset_entries = []
        for ds in datasets:
            ds_uuid     = ds.get("uuid", "")
            ds_hubmap_id = ds.get("hubmap_id", ds_uuid)
            tech        = extract_technology(ds)
            entry = {
                "id":         f"{ENTITY_API}/entities/{ds_uuid}",
                "link":       f"{PORTAL_BASE}/{ds_hubmap_id}",
                "technology": tech,
            }
            ds_label = ds.get("hubmap_id") or ds.get("lab_dataset_id") or ds.get("title")
            if ds_label:
                entry["label"] = ds_label
            dataset_entries.append(entry)

        # 5) Build sample entry
        sample: dict = {
            "sample_type":  "Tissue Block",
            "label":        block_label,
            "link":         f"{PORTAL_BASE}/{block_hubmap_id}",
            "id":           f"{ENTITY_API}/entities/{block_uuid}",
            "rui_location": rui_location,
        }
        if dataset_entries:
            sample["datasets"] = dataset_entries

        # 6) Add sample to donor bucket
        if donor_uuid not in donors:
            donor_record: dict = {
                "id":   f"{PORTAL_BASE}/{donor_uuid}",
                "link": f"{PORTAL_BASE}/{donor_uuid}",
            }
            donor_record.update(donor_info)   # sex, age, bmi where available
            donor_record["samples"] = []
            donors[donor_uuid] = donor_record
            donor_order.append(donor_uuid)
        else:
            # Backfill any info we didn't have on first encounter
            for k, v in donor_info.items():
                if k not in donors[donor_uuid]:
                    donors[donor_uuid][k] = v

        donors[donor_uuid]["samples"].append(sample)
        stats["ok"] += 1
        print(f"  ✓  Added to donor bucket ({len(donors[donor_uuid]['samples'])} block(s) so far).")

    # ── Build final YAML structure ─────────────────────────────────────────────
    registration = {
        "consortium_name": "HuBMAP",
        "provider_name":   "",          # fill in later
        "provider_uuid":   "",          # fill in later
        "defaults": {
            "id":        "",
            "link":      "",
            "thumbnail": "https://cdn.humanatlas.io/ui/ccf-eui/assets/icons/ico-unknown.svg",
        },
        "donors": [donors[uid] for uid in donor_order],
    }

    # ── Write YAML ─────────────────────────────────────────────────────────────
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(f"# yaml-language-server: $schema={SCHEMA_URL}\n\n")
        yaml.dump(
            [registration],
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )

    # ── Summary ────────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"Done.")
    print(f"  Blocks written:    {stats['ok']}")
    print(f"  Skipped (no RUI):  {stats['no_rui']}")
    print(f"  No donor found:    {stats['no_donor']}")
    print(f"  API errors:        {stats['api_err']}")
    print(f"  Unique donors:     {len(donor_order)}")
    print(f"  Output:            {args.output}")


if __name__ == "__main__":
    main()