import pandas as pd
import yaml
import sys
import os
import uuid

def csv_to_yaml(participant_csv, publication_csv, yaml_file):
    # Load the CSV data
    participants_df = pd.read_csv(participant_csv)
    publications_df = pd.read_csv(publication_csv)

    # Ensure the output directory exists
    output_dir = 'output_yaml'
    os.makedirs(output_dir, exist_ok=True)

   # Ensure the output directory exists
    output_dir = 'generated_yaml'
    os.makedirs(output_dir, exist_ok=True)

    # Process each unique Publication DOI
    for publication_doi in publications_df['Publication DOI'].unique():
        # Find all participant IDs for the current publication
        publication_rows = publications_df[publications_df['Publication DOI'] == publication_doi]
        participant_ids = publication_rows['Participant ID'].unique()
        
        # Prepare the YAML content
        yaml_content = {
            "consortium_name": "KPMP",
            "provider_name": "KPMP",
            "provider_uuid": str(uuid.uuid4()),  # Generate a unique UUID for each file
            "defaults": {
                "id": "http://example.com/required/id",
                "thumbnail": "assets/icons/ico-unknown.svg",
                "link": f"https://{publication_doi}",
                "publication": f"https://{publication_doi}"
            },
            "donors": []
        }

        # Add matching donors
        for participant_id in participant_ids:
            matching_rows = participants_df[participants_df['Participant ID'] == participant_id]
            for _, row in matching_rows.iterrows():
                donor = {
                    "id": row["Participant ID"],
                    "sex": row["Sex"],
                    "age": row["Age (Years) (Binned)"],
                    "samples": [{
                        "rui_location": "male_cortex.json" if row["Sex"] == "Male" else "female_cortex.json"
                    }]
                }
                yaml_content["donors"].append(donor)

        # Write to a YAML file
        filename = f"{publication_doi.replace('/', '_')}.yaml"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as file:
            yaml.dump(yaml_content, file, allow_unicode=True)

    print("YAML files have been created successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python csvs_to_yamls.py participant_csv.csv publication_csv.csv output_file.yaml")
        sys.exit(1)

    input_csv_file = sys.argv[1]
    output_yaml_file = sys.argv[2]

    csv_to_yaml(input_csv_file, output_yaml_file)