#!/usr/bin/env python3
import requests
import json

API_KEY = "Ag9D4NDnYemNvyJEgq8b0wB4q6q1qNbmDkDpgomBY7vW4zxW9VUpCBE4rQzjQpPy7rypayV1j0VJaBIBNX9KGH2E7by"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# Test with one of the dataset UUIDs
dataset_uuid = "ca7d5b6dda4e11e34161ff4ccb1d498c"
url = f"https://entity.api.hubmapconsortium.org/entities/{dataset_uuid}"

response = requests.get(url, headers=HEADERS)
data = response.json()

print("=== FULL JSON STRUCTURE ===")
print(json.dumps(data, indent=2))

print("\n=== CHECKING FOR ORIGIN_SAMPLES ===")
print(f"origin_samples exists: {'origin_samples' in data}")
if 'origin_samples' in data:
    print(f"origin_samples type: {type(data['origin_samples'])}")
    print(f"origin_samples length: {len(data['origin_samples'])}")
    if data['origin_samples']:
        print(f"First origin_sample keys: {data['origin_samples'][0].keys()}")
        print(f"First origin_sample organ: {data['origin_samples'][0].get('organ', 'NOT FOUND')}")

print("\n=== CHECKING FOR ORGAN ===")
upload = data.get('upload', {})
if upload:
    print(f"upload.intended_organ: {upload.get('intended_organ', 'NOT FOUND')}")

print("\n=== CHECKING FOR SEX IN TITLE ===")
title = data.get('title', '')
print(f"title: {title}")
if 'male' in title.lower():
    if 'female' in title.lower():
        print("Sex: Female")
    else:
        print("Sex: Male")
elif 'female' in title.lower():
    print("Sex: Female")
else:
    print("Sex: NOT FOUND")
