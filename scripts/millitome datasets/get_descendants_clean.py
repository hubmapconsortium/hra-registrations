#!/usr/bin/env python3
"""
Query HuBMAP Entity API descendants endpoint for each UUID
and extract Dataset descendants with their dataset_type and group_name
Uses recursive descent to drill down through Samples to find Datasets
"""

import requests
import csv
import time

# API Configuration
API_BASE = "https://entity.api.hubmapconsortium.org"
API_KEY = "Ag9D4NDnYemNvyJEgq8b0wB4q6q1qNbmDkDpgomBY7vW4zxW9VUpCBE4rQzjQpPy7rypayV1j0VJaBIBNX9KGH2E7by"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# File paths
uuid_file = "/Users/dequeue/Desktop/RUI.nosync/hra-registrations/scripts/millitome datasets/uuids.md"
output_csv = "/Users/dequeue/Desktop/RUI.nosync/hra-registrations/scripts/millitome datasets/descendants_datasets.csv"

def get_all_descendants_recursive(uuid, depth=0, max_depth=3, visited=None):
    """Recursively get all descendants, drilling down to find Datasets"""
    if visited is None:
        visited = set()
    
    if uuid in visited or depth >= max_depth:
        return []
    
    visited.add(uuid)
    url = f"{API_BASE}/descendants/{uuid}"
    
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
            print(f"    Level {depth}: {len(descendants_list)} descendants ({len(samples)} Samples, {len(datasets)} Datasets)")
        
        # If we found Samples but no Datasets, recurse into ALL Samples to find their Datasets
        if samples and not datasets:
            if depth == 0:
                print(f"      Recursing into ALL {len(samples)} samples...")
            
            # Recurse into ALL samples to get complete descendant tree
            for sample in samples:
                sample_uuid = sample.get('uuid')
                if sample_uuid:
                    time.sleep(0.05)  # Rate limiting
                    nested = get_all_descendants_recursive(sample_uuid, depth + 1, max_depth, visited)
                    all_descendants.extend(nested)
        
        return all_descendants
        
    except requests.RequestException as e:
        if depth == 0:
            print(f"      Error: {e}")
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

def get_sample_info(sample_uuid):
    """Fetch sample details to get organ and donor sex using ancestors endpoint"""
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
        
        return {
            'organ': organ,
            'sex': sex
        }
    except requests.RequestException as e:
        print(f"      Error fetching sample info for {sample_uuid}: {e}")
        return {
            'organ': 'N/A',
            'sex': 'N/A'
        }

def get_dataset_details(dataset_uuid):
    """Fetch dataset details to get group_name and status"""
    url = f"{API_BASE}/entities/{dataset_uuid}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        
        # Get group_name and status
        group_name = data.get('group_name', 'N/A')
        status = data.get('status', 'N/A')
        
        return {
            'group_name': group_name,
            'status': status
        }
    except requests.RequestException as e:
        print(f"      Error fetching details for {dataset_uuid}: {e}")
        return {
            'group_name': 'N/A',
            'status': 'N/A'
        }

# Read UUIDs
print(f"Reading UUIDs from file...")
with open(uuid_file, 'r') as f:
    uuids = [line.strip() for line in f if line.strip()]

print(f"Processing {len(uuids)} UUIDs...\n")

# Prepare CSV
csv_data = [["Original UUID", "Descendant UUID", "Dataset Type", "Group Name", "Organ", "Sex", "Status"]]

# Process each UUID
for idx, original_uuid in enumerate(uuids, 1):
    print(f"Processing {idx}/{len(uuids)}: {original_uuid}")
    
    # Get all descendants recursively (drill down through Samples to find Datasets)
    descendants = get_all_descendants_recursive(original_uuid)
    # Get organ and sex from the original sample (tissue block)
    sample_info = get_sample_info(original_uuid)
    organ = sample_info['organ']
    sex = sample_info['sex']
    
    # Extract Datasets
    datasets = extract_dataset_info(descendants)
    
    if datasets:
        print(f"  ✅ Found {len(datasets)} Dataset descendants")
        for dataset in datasets:
            # Fetch group_name and status for each dataset
            details = get_dataset_details(dataset['uuid'])
            csv_data.append([
                original_uuid, 
                dataset['uuid'], 
                dataset['dataset_type'], 
                details['group_name'],
                organ,
                sex,
                details['status']
            ])
            print(f"     - {dataset['uuid']}: {dataset['dataset_type']} ({details['group_name']}, {organ}, {sex}, {details['status']})")
            time.sleep(0.1)  # Rate limiting for detail fetches
    else:
        print(f"  ⚠️  No Dataset descendants found")
    
    # Rate limiting
    time.sleep(0.5)
    print()

# Write CSV
with open(output_csv, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(csv_data)

print(f"\n✅ Complete!")
print(f"   Processed: {len(uuids)} UUIDs")
print(f"   Found: {len(csv_data)-1} Dataset descendants")
print(f"   Output: {output_csv}")
