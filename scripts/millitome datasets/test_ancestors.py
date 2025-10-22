#!/usr/bin/env python3
import requests
import json

API_KEY = "Ag9D4NDnYemNvyJEgq8b0wB4q6q1qNbmDkDpgomBY7vW4zxW9VUpCBE4rQzjQpPy7rypayV1j0VJaBIBNX9KGH2E7by"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
API_BASE = "https://entity.api.hubmapconsortium.org"

# Test with one of the tissue block UUIDs from the YAML
sample_uuid = "cae16120c9edd555aa7d811fe94d39de"

# Try the ancestors endpoint
url = f"{API_BASE}/ancestors/{sample_uuid}"
response = requests.get(url, headers=HEADERS)
data = response.json()

print(f"=== Ancestors for {sample_uuid} ===")
print(json.dumps(data, indent=2))
