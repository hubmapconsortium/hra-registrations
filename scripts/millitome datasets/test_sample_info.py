#!/usr/bin/env python3
import requests
import json

API_KEY = "Ag9D4NDnYemNvyJEgq8b0wB4q6q1qNbmDkDpgomBY7vW4zxW9VUpCBE4rQzjQpPy7rypayV1j0VJaBIBNX9KGH2E7by"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
API_BASE = "https://entity.api.hubmapconsortium.org"

# Test with one of the tissue block UUIDs from the YAML
sample_uuid = "cae16120c9edd555aa7d811fe94d39de"

url = f"{API_BASE}/entities/{sample_uuid}"
response = requests.get(url, headers=HEADERS)
data = response.json()

print(f"=== Sample {sample_uuid} ===")
print(f"Entity type: {data.get('entity_type')}")
print(f"Organ: {data.get('organ', 'NOT FOUND')}")
print(f"\nDirect ancestors:")
direct_ancestors = data.get('direct_ancestors', [])
for ancestor in direct_ancestors:
    print(f"  - {ancestor.get('entity_type')}: {ancestor.get('uuid')}")
    if ancestor.get('entity_type') == 'Donor':
        mapped_metadata = ancestor.get('mapped_metadata', {})
        print(f"    Sex: {mapped_metadata.get('sex', 'NOT FOUND')}")
