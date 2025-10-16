#!/usr/bin/env python3
import requests
import json

API_BASE = "https://entity.api.hubmapconsortium.org"
API_KEY = "AgvKjD7WE0nwzVnorzQEaO6Vbry35OvOjJVKYnjo529lBYrO23HzCk4nb5pDwD1b2z2ONgej18nDnrsOMmwdaTmBQNV"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

uuid = "a65abda3a052081a8068af0536a56cc1"
url = f"{API_BASE}/descendants/{uuid}"

print(f"Getting descendants for: {uuid}\n")

response = requests.get(url, headers=HEADERS)
data = response.json()

print(f"Total items returned: {len(data)}\n")

# Show first 3 items with their entity_type
print("First 3 items:")
for i, item in enumerate(data[:3]):
    print(f"\n  Item {i+1}:")
    print(f"    entity_type: {item.get('entity_type')}")
    print(f"    uuid: {item.get('uuid')}")
    if item.get('entity_type') == 'Dataset':
        print(f"    data_types: {item.get('data_types')}")
    
print("\n" + "="*80)

# Find all datasets
datasets = []
for item in data:
    if item.get("entity_type") == "Dataset":
        datasets.append({
            "uuid": item.get("uuid"),
            "data_types": item.get("data_types", [])
        })

print(f"\nFound {len(datasets)} Datasets")
