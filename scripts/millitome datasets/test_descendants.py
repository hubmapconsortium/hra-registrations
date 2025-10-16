#!/usr/bin/env python3
import requests
import json

API_BASE = "https://entity.api.hubmapconsortium.org"
API_KEY = "AgvKjD7WE0nwzVnorzQEaO6Vbry35OvOjJVKYnjo529lBYrO23HzCk4nb5pDwD1b2z2ONgej18nDnrsOMmwdaTmBQNV"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# Test with the UUID you mentioned
uuid = "a65abda3a052081a8068af0536a56cc1"
url = f"{API_BASE}/descendants/{uuid}"

print(f"Testing UUID: {uuid}")
print(f"URL: {url}\n")

response = requests.get(url, headers=HEADERS)
print(f"Status Code: {response.status_code}\n")

data = response.json()

print(f"Response type: {type(data)}")
print(f"Response is list: {isinstance(data, list)}")

if isinstance(data, list):
    print(f"Number of descendants: {len(data)}\n")
    
    # Check entity types
    entity_types = {}
    dataset_count = 0
    first_dataset = None
    
    for item in data:
        etype = item.get('entity_type', 'Unknown')
        entity_types[etype] = entity_types.get(etype, 0) + 1
        
        if etype == 'Dataset' and first_dataset is None:
            first_dataset = item
            dataset_count += 1
    
    print("Entity type breakdown:")
    for etype, count in sorted(entity_types.items()):
        print(f"  {etype}: {count}")
    
    if first_dataset:
        print(f"\nFirst Dataset found:")
        print(f"  UUID: {first_dataset.get('uuid')}")
        print(f"  dataset_type: {first_dataset.get('dataset_type')}")
        print(f"  All keys: {list(first_dataset.keys())}")
    else:
        print("\n❌ NO DATASETS FOUND!")
        print("Sample of first descendant:")
        if len(data) > 0:
            print(json.dumps(data[0], indent=2)[:500])
