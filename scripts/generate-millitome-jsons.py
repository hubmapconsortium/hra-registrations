#!/usr/bin/env python3
"""
Copy millitome registration JSON files, renamed to their HuBMAP IDs.

Usage:
    python copy_registrations.py <excel_file> <millitome_dir> <output_dir>

Arguments:
    excel_file     Path to the RUI hubmap blocks Excel spreadsheet
    millitome_dir  Path to the local millitome directory in the cloned hra-amap repo
                   (e.g., /path/to/hra-amap/output-data/millitome)
    output_dir     Destination directory for the renamed hubmap_id.json files
"""

import sys
import os
import shutil
import re
import pandas as pd


SIZE_MAP = {1: "small", 2: "medium", 3: "large"}
SEX_MAP = {"M": "male", "F": "female"}


def strip_donor_prefix(lab_id):
    """Strip the leading D###- from a lab_tissue_sample_id.
    e.g. D115-RLL-10A3 -> RLL-10A3
    """
    return re.sub(r'^D\d+-', '', lab_id)


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)

    excel_path = sys.argv[1]
    millitome_dir = sys.argv[2]
    output_dir = sys.argv[3]

    if not os.path.isfile(excel_path):
        print(f"ERROR: Excel file not found: {excel_path}")
        sys.exit(1)
    if not os.path.isdir(millitome_dir):
        print(f"ERROR: Millitome directory not found: {millitome_dir}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_excel(excel_path, header=0)
    col_hubmap = df.columns[0]   # Column A - hubmap_id
    col_size = df.columns[1]     # Column B - millitome size (1,2,3)
    col_sex = df.columns[3]      # Column D - Sex
    col_lab_id = df.columns[8]   # Column I - lab_tissue_sample_id

    copied = 0
    skipped = 0
    errors = 0

    for idx, row in df.iterrows():
        row_num = idx + 2  # Excel row (1-indexed header + 1-indexed data)

        # Skip if column B is empty
        if pd.isna(row[col_size]):
            skipped += 1
            continue

        size_val = int(row[col_size])
        sex_val = str(row[col_sex]).strip().upper()
        hubmap_id = str(row[col_hubmap]).strip()
        lab_id = str(row[col_lab_id]).strip()

        # Validate size
        if size_val not in SIZE_MAP:
            print(f"WARNING (row {row_num}): Invalid size value '{size_val}', skipping.")
            errors += 1
            continue

        # Validate sex
        if sex_val not in SEX_MAP:
            print(f"WARNING (row {row_num}): Invalid sex value '{sex_val}', skipping.")
            errors += 1
            continue

        size_str = SIZE_MAP[size_val]
        sex_str = SEX_MAP[sex_val]
        stripped_id = strip_donor_prefix(lab_id)

        # Build path: lung-{sex}-{size}/v1.0/registrations/{stripped_id}.json
        json_filename = f"{stripped_id}.json"
        source_path = os.path.join(
            millitome_dir,
            f"lung-{sex_str}-{size_str}",
            "v1.0",
            "registrations",
            json_filename
        )

        dest_path = os.path.join(output_dir, f"{hubmap_id}.json")

        if not os.path.isfile(source_path):
            print(f"ERROR (row {row_num}): JSON not found: {source_path}")
            errors += 1
            continue

        shutil.copy2(source_path, dest_path)
        copied += 1

    print(f"\nDone. Copied: {copied} | Skipped (no size): {skipped} | Errors: {errors}")


if __name__ == "__main__":
    main()