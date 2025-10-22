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

# Cache for sample info and dataset info to avoid repeated API calls
sample_info_cache = {}
dataset_info_cache = {}

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

def get_dataset_status(dataset_uuid):
    """Fetch dataset status"""
    if dataset_uuid in dataset_info_cache:
        return dataset_info_cache[dataset_uuid]
    
    url = f"{API_BASE}/entities/{dataset_uuid}"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        status = data.get('status', 'N/A')
        dataset_info_cache[dataset_uuid] = status
        return status
    except requests.RequestException as e:
        # Don't print error here, will be printed in calling function
        dataset_info_cache[dataset_uuid] = 'Error'
        raise e

# Read the CSV
print(f"Reading CSV from {input_csv}...")
with open(input_csv, 'r') as f:
    reader = csv.reader(f)
    rows = list(reader)

header = rows[0]
data_rows = rows[1:]

# Add Status column to header if it doesn't exist
if 'Status' not in header:
    header.append('Status')

print(f"Found {len(data_rows)} rows")

# Process rows
fixed_rows = [header]
unique_samples = set()
unique_datasets = set()
rows_needing_fix = 0

# First pass - count rows needing fixes and collect all datasets
for row in data_rows:
    original_uuid = row[0]
    descendant_uuid = row[1]
    organ = row[4] if len(row) > 4 else 'N/A'
    sex = row[5] if len(row) > 5 else 'N/A'
    
    if organ == 'N/A' or sex == 'N/A':
        rows_needing_fix += 1
        unique_samples.add(original_uuid)
    
    # Need to fetch status for ALL datasets
    unique_datasets.add(descendant_uuid)

print(f"Rows with N/A organ/sex values: {rows_needing_fix}")
print(f"Unique sample UUIDs needing lookup: {len(unique_samples)}")
print(f"Unique datasets needing status lookup: {len(unique_datasets)}")
print(f"\nFetching sample info...")

# Prefetch all sample info
for idx, sample_uuid in enumerate(unique_samples, 1):
    print(f"  Fetching sample {idx}/{len(unique_samples)}: {sample_uuid}")
    get_sample_info(sample_uuid)
    time.sleep(0.1)  # Rate limiting

# Prefetch dataset status for ALL datasets
print(f"\nFetching dataset status...")
total_datasets = len(unique_datasets)
error_count = 0
for idx, dataset_uuid in enumerate(unique_datasets, 1):
    if idx % 50 == 0 or idx == 1:
        print(f"  Fetching dataset status {idx}/{total_datasets} ({100*idx/total_datasets:.1f}%) - Errors: {error_count}...")
    try:
        get_dataset_status(dataset_uuid)
        time.sleep(0.02)  # Reduced rate limiting
    except Exception as e:
        error_count += 1
        print(f"    Error on dataset {idx} ({dataset_uuid}): {str(e)[:100]}")
        time.sleep(0.1)  # Longer delay on error
        continue  # Continue processing other datasets

print(f"\nUpdating CSV rows...")

# Second pass - update rows
for idx, row in enumerate(data_rows, 1):
    original_uuid = row[0]
    descendant_uuid = row[1]
    dataset_type = row[2]
    group_name = row[3]
    organ = row[4] if len(row) > 4 else 'N/A'
    sex = row[5] if len(row) > 5 else 'N/A'
    
    # If organ or sex is N/A, get from sample
    if organ == 'N/A' or sex == 'N/A':
        sample_info = sample_info_cache.get(original_uuid, {'organ': 'N/A', 'sex': 'N/A'})
        if organ == 'N/A':
            organ = sample_info['organ']
        if sex == 'N/A':
            sex = sample_info['sex']
    
    # Get status from dataset
    status = dataset_info_cache.get(descendant_uuid, 'N/A')
    
    if idx % 100 == 0:
        print(f"  Processed {idx}/{len(data_rows)} rows...")
    
    fixed_rows.append([original_uuid, descendant_uuid, dataset_type, group_name, organ, sex, status])

# Write updated CSV
print(f"\nWriting fixed CSV to {output_csv}...")
with open(output_csv, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(fixed_rows)

print(f"\n✅ Complete!")
print(f"   Original rows: {len(data_rows)}")
print(f"   Fixed rows: {len(fixed_rows) - 1}")
print(f"   Output: {output_csv}")
