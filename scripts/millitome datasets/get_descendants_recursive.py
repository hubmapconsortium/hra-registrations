#!/usr/bin/env python3
"""
Get ALL descendants recursively to find Dataset descendants
"""
import requests
import csv
import time
from collections import deque

# API Configuration
API_BASE = "https://entity.api.hubmapconsortium.org"
API_KEY = "AgvKjD7WE0nwzVnorzQEaO6Vbry35OvOjJVKYnjo529lBYrO23HzCk4nb5pDwD1b2z2ONgej18nDnrsOMmwdaTmBQNV"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# File paths
uuid_file = "/Users/dequeue/Desktop/cae16120c9edd555aa7d811fe94d39de/cae16120c9edd555aa7d811fe94d39de.md"
output_csv = "/Users/dequeue/Desktop/RUI.nosync/hra-registrations/descendants_datasets.csv"

def get_descendants(uuid):
    """Get direct descendants for a given UUID"""
    url = f"{API_BASE}/descendants/{uuid}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json() if isinstance(response.json(), list) else []
    except Exception:
        return []

def get_all_dataset_descendants(root_uuid):
    """Recursively get all Dataset descendants"""
    datasets = []
    visited = set()
    queue = deque([root_uuid])
    
    while queue:
        current_uuid = queue.popleft()
        
        if current_uuid in visited:
            continue
        visited.add(current_uuid)
        
        # Get descendants
        descendants = get_descendants(current_uuid)
        
        for desc in descendants:
            desc_uuid = desc.get("uuid")
            entity_type = desc.get("entity_type")
            
            if not desc_uuid:
                continue
            
            if entity_type == "Dataset":
                # Found a dataset!
                dataset_type = desc.get("dataset_type", "")
                datasets.append((desc_uuid, dataset_type))
            elif entity_type == "Sample":
                # Need to check this sample's descendants
                if desc_uuid not in visited:
                    queue.append(desc_uuid)
        
        # Rate limiting
        time.sleep(0.2)
    
    return datasets

# Read UUIDs
print("Reading UUIDs...")
with open(uuid_file, 'r') as f:
    uuids = [line.strip() for line in f if line.strip()]

print(f"Processing {len(uuids)} UUIDs (this may take a while)...\n")

# Prepare CSV
csv_data = [["Original UUID", "Descendant UUID", "Dataset Type"]]

# Process each UUID
for idx, original_uuid in enumerate(uuids, 1):
    print(f"[{idx}/{len(uuids)}] {original_uuid}...", end=" ", flush=True)
    
    # Get all dataset descendants (recursively)
    datasets = get_all_dataset_descendants(original_uuid)
    
    # Add to CSV
    for desc_uuid, dataset_type in datasets:
        csv_data.append([original_uuid, desc_uuid, dataset_type])
    
    print(f"✓ {len(datasets)} dataset(s)")

# Write CSV
with open(output_csv, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(csv_data)

print(f"\n✅ Complete!")
print(f"   Processed: {len(uuids)} UUIDs")
print(f"   Found: {len(csv_data)-1} Dataset descendants")
print(f"   Output: {output_csv}")
