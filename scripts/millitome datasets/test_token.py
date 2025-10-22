#!/usr/bin/env python3
import requests

API_KEY = "Ag9D4NDnYemNvyJEgq8b0wB4q6q1qNbmDkDpgomBY7vW4zxW9VUpCBE4rQzjQpPy7rypayV1j0VJaBIBNX9KGH2E7by"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# Test dataset UUID
url = "https://entity.api.hubmapconsortium.org/entities/ca7d5b6dda4e11e34161ff4ccb1d498c"

try:
    response = requests.get(url, headers=HEADERS)
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Dataset status: {data.get('status', 'NOT FOUND')}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
