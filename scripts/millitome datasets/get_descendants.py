#!/usr/bin/env python3
"""
Query HuBMAP Entity API descendants endpoint for each UUID
and extract Dataset descendants with their dataset_type
"""

import requests
import csv
import time

# API Configuration
API_BASE = "https://entity.api.hubmapconsortium.org"
API_KEY = "AgvKjD7WE0nwzVnorzQEaO6Vbry35OvOjJVKYnjo529lBYrO23HzCk4nb5pDwD1b2z2ONgej18nDnrsOMmwdaTmBQNV"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# Read UUIDs from file
uuid_file = "/Users/dequeue/Desktop/cae16120c9edd555aa7d811fe94d39de/cae16120c9edd555aa7d811fe94d39de.md"
output_csv = "/Users/dequeue/Desktop/RUI.nosync/hra-registrations/descendants_datasets.csv"

def get_all_descendants_recursive(uuid, depth=0, max_depth=3, visited=None):
    """Recursively get all descendants, drilling down to find Datasets"""
    if visited is None:
        visited = set()
    
    if uuid in visited or depth >= max_depth:
        return []
    
    visited.add(uuid)
    url = f"{API_BASE}/descendants/{uuid}"
    indent = '  ' * depth
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        
        descendants_list = data.get('descendants', []) if isinstance(data, dict) else data
        
        if not descendants_list:
            return []
        
        all_descendants = list(descendants_list)
        
        # Count entity types
        samples = [d for d in descendants_list if d.get('entity_type') == 'Sample']
        datasets = [d for d in descendants_list if d.get('entity_type') == 'Dataset']
        
        if depth == 0:
            print(f"    {indent}Level {depth}: {len(descendants_list)} descendants ({len(samples)} Samples, {len(datasets)} Datasets)")
        
        # If we found Samples but no Datasets, recurse into Samples to find their Datasets
        if samples and not datasets:
            if depth == 0:
                print(f"    {indent}  Recursing into {min(len(samples), 10)} samples...")
            
            # Only recurse into a subset to avoid explosion
            for i, sample in enumerate(samples[:10], 1):  # Limit to first 10 samples
                sample_uuid = sample.get('uuid')
                if sample_uuid:
                    time.sleep(0.05)  # Rate limiting
                    nested = get_all_descendants_recursive(sample_uuid, depth + 1, max_depth, visited)
                    all_descendants.extend(nested)
        
        return all_descendants
        
    except requests.RequestException as e:
        if depth == 0:
            print(f"    {indent}Error: {e}")
        return []

def extract_dataset_info(descendants_list):
    """Extract only Dataset information from descendants list"""
    datasets = []
    for desc in descendants_list:
        if desc.get('entity_type') == 'Dataset':
            datasets.append({
                'uuid': desc.get('uuid'),
                'dataset_type': desc.get('dataset_type', 'N/A')
            })
    return datasets

# Read UUIDs from file
print(f"Reading UUIDs from {uuid_file}")
with open(uuid_file, 'r') as f:
    uuids = [line.strip() for line in f if line.strip()]

print(f"Found {len(uuids)} UUIDs to process")

# Prepare CSV output
csv_data = []
csv_data.append(["Original UUID", "Descendant UUID", "Dataset Type"])

# Process each UUID
total = len(uuids)
for idx, original_uuid in enumerate(uuids, 1):
    print(f"\nProcessing {idx}/{total}: {original_uuid}")
    
    # Get all descendants recursively (drill down through Samples to find Datasets)
    descendants = get_all_descendants_recursive(original_uuid)
    
    if descendants:
        # Extract Dataset descendants
        datasets = extract_dataset_info(descendants)
        
        if datasets:
            print(f"  ✅ Found {len(datasets)} Dataset descendants")
            for dataset in datasets:
                csv_data.append([original_uuid, dataset['uuid'], dataset['dataset_type']])
                print(f"     - {dataset['uuid']}: {dataset['dataset_type']}")
        else:
            print(f"  ⚠️  No Dataset descendants found")
            # Show first descendant for debugging
            if len(descendants) > 0:
                first = descendants[0]
                print(f"     First descendant entity_type: {first.get('entity_type')}")
    else:
        print(f"  ❌ No descendants returned")
    
    # Rate limiting - be nice to the API
    if idx < total:
        time.sleep(0.5)

# Write CSV file
print(f"\nWriting results to {output_csv}")
with open(output_csv, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(csv_data)

print(f"\n✅ Complete! Processed {total} UUIDs")
print(f"   Found {len(csv_data) - 1} total Dataset descendants")
print(f"   Output: {output_csv}")
