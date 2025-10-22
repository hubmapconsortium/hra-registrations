#!/usr/bin/env python3
"""
Simply add status column to existing CSV
"""

import requests
import csv
import time

# API Configuration
API_BASE = "https://entity.api.hubmapconsortium.org"
API_KEY = "Ag9D4NDnYemNvyJEgq8b0wB4q6q1qNbmDkDpgomBY7vW4zxW9VUpCBE4rQzjQpPy7rypayV1j0VJaBIBNX9KGH2E7by"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

input_csv = "/Users/dequeue/Desktop/RUI.nosync/hra-registrations/scripts/millitome datasets/descendants_datasets.csv"
output_csv = "/Users/dequeue/Desktop/RUI.nosync/hra-registrations/scripts/millitome datasets/descendants_datasets_with_status.csv"

print("Reading CSV...")
with open(input_csv, 'r') as f:
    reader = csv.reader(f)
    rows = list(reader)

header = rows[0]
header.append('Status')
data_rows = rows[1:]

print(f"Processing {len(data_rows)} rows...")

output_rows = [header]

for idx, row in enumerate(data_rows, 1):
    dataset_uuid = row[1]  # Descendant UUID column
    
    print(f"  {idx}/{len(data_rows)} - Fetching {dataset_uuid}...", flush=True)
    
    # Fetch status
    try:
        url = f"{API_BASE}/entities/{dataset_uuid}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        status = data.get('status', 'N/A')
        print(f"    Status: {status}", flush=True)
    except Exception as e:
        status = 'Error'
        print(f"    Error: {str(e)[:50]}", flush=True)
    
    row.append(status)
    output_rows.append(row)
    
    time.sleep(0.02)

print(f"\nWriting to {output_csv}...")
with open(output_csv, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(output_rows)

print(f"Done! {len(output_rows)-1} rows")
