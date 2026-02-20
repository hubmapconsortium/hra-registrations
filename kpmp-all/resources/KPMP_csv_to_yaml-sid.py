import pandas as pd
import yaml
import uuid
from collections import defaultdict

def generate_uuid():
    return str(uuid.uuid4())

def get_rui_location(sex, location, laterality):
    location_map = {
        ('Male', 'Left', 'Upper pole'): 'male-upper-left-pole.json',
        ('Male', 'Left', 'Middle'): 'male-mid-left.json',
        ('Male', 'Left', 'Lower pole'): 'male-lower-left-pole.json',
        ('Male', 'Right', 'Upper pole'): 'male-upper-right-pole.json',
        ('Male', 'Right', 'Middle'): 'male-mid-right.json',
        ('Male', 'Right', 'Lower pole'): 'male-lower-right-pole.json',
        ('Female', 'Left', 'Upper pole'): 'female-upper-left-pole.json',
        ('Female', 'Left', 'Middle'): 'female-mid-left.json',
        ('Female', 'Left', 'Lower pole'): 'female-lower-left-pole.json',
        ('Female', 'Right', 'Upper pole'): 'female-upper-right-pole.json',
        ('Female', 'Right', 'Middle'): 'female-mid-right.json',
        ('Female', 'Right', 'Lower pole'): 'female-lower-right-pole.json',
    }
    return location_map.get((sex, location, laterality), 'unknown-location.json')

def process_kpmp_csv(input_csv_path, output_yaml_path):
    # Load and clean CSV
    df = pd.read_csv(input_csv_path)
    df = df.dropna(subset=['filter active in Repository', 'filter active in Spatial Viewer'])
    df = df[(df['filter active in Repository'].astype(str).str.strip() != '') &
            (df['filter active in Spatial Viewer'].astype(str).str.strip() != '')]

    # Initial YAML structure
    base_yaml = {
        "consortium_name": "KPMP",
        "provider_name": "KPMP",
        "provider_uuid": generate_uuid(),
        "defaults": {
            "id": generate_uuid(),
            "thumbnail": "https://cdn.humanatlas.io/ui/ccf-eui/assets/icons/ico-unknown.svg",
            "link": "https://atlas.kpmp.org/"
        },
        "donors": []
    }

    grouped_donors = defaultdict(lambda: defaultdict(lambda: {
        "datasets": []
    }))

    for _, row in df.iterrows():
        donor_id = "https://atlas.kpmp.org/#" + str(row["Participant ID"])
        sex = row["Sex"]
        label = str(row["Participant ID"]) + ", " + str(row["Age (Years) (Binned)"])
        rui_location = get_rui_location(row["Sex"], row["Location"], row["Laterality"])
        donor_key = (donor_id, sex, label)

        dataset = {
            "link": str(row["Formula: KPMP Atlas Spatial Viewer Link"]),
            "technology": str(row["tech name"]),
            "id": str(row["Formula: KPMP Atlas Spatial Viewer Link"]) + "/#" + str(row["Participant ID"])
        }

        grouped_donors[donor_key][rui_location]["datasets"].append(dataset)

    for (donor_id, sex, label), rui_groups in grouped_donors.items():
        samples = []
        for rui_location, sample_data in rui_groups.items():
            samples.append({
                "rui_location": rui_location,
                "datasets": sample_data["datasets"]
            })
        base_yaml["donors"].append({
            "id": donor_id,
            "sex": sex,
            "label": label,
            "samples": samples
        })

    # Write final YAML
    with open(output_yaml_path, 'w') as f:
        f.write("# yaml-language-server: $schema=https://raw.githubusercontent.com/hubmapconsortium/hra-rui-locations-processor/main/registrations.schema.json\n\n")
        yaml.dump([base_yaml], f, allow_unicode=True, sort_keys=False, default_flow_style=False)

    print(f"✅ Final YAML file saved to: {output_yaml_path}")

# Usage:
input_csv = "HuBMAP Healthy Tissue Registry Deep Links.csv"
output_yaml = "HuBMAP_Healthy_Tissue_Registry_Deep_Links_output.yaml"
process_kpmp_csv(input_csv, output_yaml)
