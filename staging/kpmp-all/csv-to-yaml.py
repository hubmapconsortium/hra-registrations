import pandas as pd
import yaml
import sys
import os

def csv_to_yaml(csv_file, yaml_file):

    # Check if the YAML file already exists
    # Initialize an empty structure or read the existing YAML file
    yaml_data = {}
    if os.path.exists(yaml_file):
        with open(yaml_file, 'r') as file:
            yaml_data = yaml.safe_load(file) or {}

    # Ensure 'donors' key is in yaml_data and clear its contents
    yaml_data['donors'] = []

    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Base structure for the YAML file
    yaml_data = {
        "donors": []
    }

    for _, row in df.iterrows():
        # Create donor entry
        donor = {
            "id": row["Participant ID"],
            "sex": row["Sex"],
            "age": row["Age (Years) (Binned)"],
            "samples": [{
                "rui_location": "male_cortex.json" if row["Sex"] == "Male" else "female_cortex.json"
            }]
        }

        # Append to the list of donors
        yaml_data["donors"].append(donor)

    # Write to YAML file
    with open(yaml_file, 'w') as file:
        yaml.dump(yaml_data, file, sort_keys=False, default_flow_style=False, indent=2)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python csv_to_yaml.py input_file.csv output_file.yaml")
        sys.exit(1)

    input_csv_file = sys.argv[1]
    output_yaml_file = sys.argv[2]

    csv_to_yaml(input_csv_file, output_yaml_file)