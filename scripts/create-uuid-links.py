import yaml
import requests
import argparse

def update_yaml_with_uuids(filepath, token):
    headers = {"Authorization": f"Bearer {token}"}
    entity_api_base = "https://entity.api.hubmapconsortium.org/entities"

    # Load YAML
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)

    # Process each sample
    for provider in data:
        for donor in provider.get("donors", []):
            for sample in donor.get("samples", []):
                hubmap_id = sample["id"].split("/")[-1]
                url = f"{entity_api_base}/{hubmap_id}"
                response = requests.get(url, headers=headers)
                if response.ok:
                    uuid = response.json().get("uuid")
                    if uuid:
                        sample["id"] = f"{entity_api_base}/{uuid}"
                        print(f"Updated: {hubmap_id} → {uuid}")
                    else:
                        print(f"Warning: No UUID found for {hubmap_id}")
                else:
                    print(f"Error: Failed to fetch entity for {hubmap_id} — {response.status_code}")

    # Save back to same file
    with open(filepath, "w") as f:
        yaml.dump(data, f, sort_keys=False)

    print(f"\n✅ YAML successfully updated at: {filepath}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update HuBMAP sample IDs in a YAML file using the Entity API.")
    parser.add_argument("token", help="HuBMAP Entity API token")
    parser.add_argument("yaml_file", help="Path to YAML file to update (will be overwritten)")

    args = parser.parse_args()
    update_yaml_with_uuids(args.yaml_file, args.token)