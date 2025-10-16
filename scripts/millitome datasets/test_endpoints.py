#!/usr/bin/env python3
import requests
import json

API_BASE = "https://entity.api.hubmapconsortium.org"
API_KEY = "AgvKjD7WE0nwzVnorzQEaO6Vbry35OvOjJVKYnjo529lBYrO23HzCk4nb5pDwD1b2z2ONgej18nDnrsOMmwdaTmBQNV"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

uuid = "a65abda3a052081a8068af0536a56cc1"

# Try different endpoints
endpoints = [
    f"/descendants/{uuid}",
    f"/descendants/{uuid}?property=uuid",
    f"/entities/{uuid}/descendants",
    f"/entities/{uuid}",
]

for endpoint in endpoints:
    url = f"{API_BASE}{endpoint}"
    print(f"\n{'='*80}")
    print(f"Testing: {url}")
    print('='*80)
    
    try:
        response = requests.get(url, headers=HEADERS)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                print(f"Response: List with {len(data)} items")
                # Check for datasets in list
                datasets = [item for item in data if isinstance(item, dict) and item.get('entity_type') == 'Dataset']
                print(f"Datasets found: {len(datasets)}")
                if datasets:
                    print(f"First dataset UUID: {datasets[0].get('uuid')}")
                    print(f"First dataset type: {datasets[0].get('dataset_type')}")
                    
            elif isinstance(data, dict):
                print(f"Response: Dict with keys: {list(data.keys())[:10]}")
                
                # Check if it has descendants field
                if 'descendants' in data:
                    desc = data['descendants']
                    print(f"  'descendants' field type: {type(desc)}")
                    if isinstance(desc, list):
                        print(f"  'descendants' length: {len(desc)}")
                        datasets = [item for item in desc if isinstance(item, dict) and item.get('entity_type') == 'Dataset']
                        print(f"  Datasets in descendants: {len(datasets)}")
                        
                # Check if entity itself has dataset info
                if data.get('entity_type') == 'Dataset':
                    print(f"  This entity IS a dataset!")
                    print(f"  dataset_type: {data.get('dataset_type')}")
                    
    except Exception as e:
        print(f"Error: {e}")
