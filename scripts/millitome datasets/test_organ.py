#!/usr/bin/env python3
import requests
import json

API_KEY = "Ag9D4NDnYemNvyJEgq8b0wB4q6q1qNbmDkDpgomBY7vW4zxW9VUpCBE4rQzjQpPy7rypayV1j0VJaBIBNX9KGH2E7by"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# Test with a few dataset UUIDs - one with organ and one without
test_uuids = [
    "547348cdd22c40ec5620c0320c5516ab",  # Has UT
    "163e9dbe4b60239d765e5d1cbcfe22c4",  # N/A
]

for uuid in test_uuids:
    url = f"https://entity.api.hubmapconsortium.org/entities/{uuid}"
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    
    print(f"\n=== Dataset {uuid} ===")
    print(f"Title: {data.get('title', 'N/A')}")
    
    # Check upload.intended_organ
    upload = data.get('upload', {})
    if upload:
        print(f"upload exists: True")
        print(f"upload.intended_organ: {upload.get('intended_organ', 'NOT FOUND')}")
    else:
        print(f"upload exists: False")
    
    # Check if there's organ info elsewhere
    print(f"Keys in data: {list(data.keys())}")
