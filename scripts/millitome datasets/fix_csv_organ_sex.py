#!/usr/bin/env python3
"""
Fix the CSV by filling in N/A organ and sex values using the ancestors endpoint
"""

import requests
import csv
import time

# API Configuration
API_BASE = "https://entity.api.hubmapconsortium.org"
API_KEY = "Ag9D4NDnYemNvyJEgq8b0wB4q6q1qNbmDkDpgomBY7vW4zxW9VUpCBE4rQzjQpPy7rypayV1j0VJaBIBNX9KGH2E7by"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# File paths
input_csv = "/Users/dequeue/Desktop/RUI.nosync/hra-registrations/scripts/millitome datasets/descendants_datasets.csv"
output_csv = "/Users/dequeue/Desktop/RUI.nosync/hra-registrations/scripts/millitome datasets/descendants_datasets_fixed.csv"

# Cache for sample info to avoid repeated API calls
sample_info_cache = {}

def get_sample_info(sample_uuid):
    """Fetch sample details to get organ and donor sex using ancestors endpoint"""
    if sample_uuid in sample_info_cache:
        return sample_info_cache[sample_uuid]
    
    url = f"{API_BASE}/ancestors/{sample_uuid}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        ancestors = response.json()
        
        organ = 'N/A'
        sex = 'N/A'
        
        # ancestors is a list of entities
        for ancestor in ancestors:
            # Get organ from organ sample
            if ancestor.get('entity_type') == 'Sample' and ancestor.get('sample_category') == 'organ':
                organ = ancestor.get('organ', 'N/A')
            
            # Get sex from donor
            if ancestor.get('entity_type') == 'Donor':
                metadata = ancestor.get('metadata', {})
                organ_donor_data = metadata.get('organ_donor_data', [])
                for data_item in organ_donor_data:
                    if data_item.get('grouping_concept_preferred_term') == 'Sex':
                        sex = data_item.get('data_value', 'N/A')
                        break
        
        result = {'organ': organ, 'sex': sex}
        sample_info_cache[sample_uuid] = result
        return result
    except requests.RequestException as e:
        print(f"      Error fetching sample info for {sample_uuid}: {e}")
        return {'organ': 'N/A', 'sex': 'N/A'}

# Read the CSV
print(f"Reading CSV from {input_csv}...")
with open(input_csv, 'r') as f:
    reader = csv.reader(f)
    rows = list(reader)

header = rows[0]
data_rows = rows[1:]

print(f"Found {len(data_rows)} rows")

# Process rows
fixed_rows = [header]
unique_samples = set()
rows_needing_fix = 0

# First pass - count rows needing fixes
for row in data_rows:
    original_uuid = row[0]
    organ = row[4]
    sex = row[5]
    
    if organ == 'N/A' or sex == 'N/A':
        rows_needing_fix += 1
        unique_samples.add(original_uuid)

print(f"Rows with N/A values: {rows_needing_fix}")
print(f"Unique sample UUIDs needing lookup: {len(unique_samples)}")
print(f"\nFetching sample info...")

# Prefetch all sample info
for idx, sample_uuid in enumerate(unique_samples, 1):
    print(f"  Fetching {idx}/{len(unique_samples)}: {sample_uuid}")
    get_sample_info(sample_uuid)
    time.sleep(0.1)  # Rate limiting

print(f"\nUpdating CSV rows...")

# Second pass - update rows
for idx, row in enumerate(data_rows, 1):
    original_uuid = row[0]
    descendant_uuid = row[1]
    dataset_type = row[2]
    group_name = row[3]
    organ = row[4]
    sex = row[5]
    
    # If organ or sex is N/A, get from sample
    if organ == 'N/A' or sex == 'N/A':
        sample_info = sample_info_cache.get(original_uuid, {'organ': 'N/A', 'sex': 'N/A'})
        if organ == 'N/A':
            organ = sample_info['organ']
        if sex == 'N/A':
            sex = sample_info['sex']
        
        if idx % 100 == 0:
            print(f"  Processed {idx}/{len(data_rows)} rows...")
    
    fixed_rows.append([original_uuid, descendant_uuid, dataset_type, group_name, organ, sex])

# Write updated CSV
print(f"\nWriting fixed CSV to {output_csv}...")
with open(output_csv, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(fixed_rows)

print(f"\n✅ Complete!")
print(f"   Original rows: {len(data_rows)}")
print(f"   Fixed rows: {len(fixed_rows) - 1}")
print(f"   Output: {output_csv}")
