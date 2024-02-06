import pandas as pd
import yaml
import os
import uuid
import sys

def generate_yamls(participant_csv, publication_csv, output_dir):
    def generate_uuid():
        return str(uuid.uuid4())

    participants_df = pd.read_csv(participant_csv)
    publications_df = pd.read_csv(publication_csv)

    # Ensure DOIs are treated as strings and handle NaN values
    publications_df['Data DOI'] = publications_df['Data DOI'].apply(lambda x: str(x) if not pd.isnull(x) else 'unknown')
    publications_df['Publication DOI'] = publications_df['Publication DOI'].apply(lambda x: str(x) if not pd.isnull(x) else '')

    os.makedirs(output_dir, exist_ok=True)

    # Initialize a counter for the number of YAML files created
    yaml_count = 0

    for data_doi in publications_df['Data DOI'].unique():
        # Skip processing if DOI is 'unknown'
        if data_doi == 'unknown':
            continue

        yaml_content = {
            "# yaml-language-server: $schema=https://raw.githubusercontent.com/hubmapconsortium/hra-rui-locations-processor/main/registrations.schema.json"
            "consortium_name": "KPMP",
            "provider_name": "KPMP",
            "provider_uuid": generate_uuid(),
            "defaults": {
                "id": "http://example.com/required/id",
                "thumbnail": "assets/icons/ico-unknown.svg",
                "link": f"https://doi.org/{data_doi}",
                "publication": ""
            },
            "donors": []
        }

        matching_publication_rows = publications_df[publications_df['Data DOI'] == data_doi]
        
        for _, pub_row in matching_publication_rows.iterrows():
            participant_id = pub_row['Participant ID']
            if 'Publication DOI' in pub_row and pub_row['Publication DOI']:
                yaml_content["defaults"]["publication"] = f"https://doi.org/{pub_row['Publication DOI']}"
            matching_participant_rows = participants_df[participants_df['Participant ID'] == participant_id]
            for _, part_row in matching_participant_rows.iterrows():
                donor = {
                    "id": part_row["Participant ID"],
                    "sex": part_row["Sex"],
                    "age": part_row["Age (Years) (Binned)"],
                    "samples": [{
                        "rui_location": "male_cortex.json" if part_row["Sex"] == "Male" else "female_cortex.json"
                    }]
                }
                yaml_content["donors"].append(donor)

        filename = f"{data_doi.replace('/', '_')}.yaml"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as file:
            yaml.dump(yaml_content, file, allow_unicode=True, sort_keys=False)
        yaml_count += 1  # Increment the counter after successful YAML creation

    # Update the print statement to reflect the number of YAML files created
    print(f"{yaml_count} YAML files have been created successfully.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python generate_yamls.py <Participant CSV> <Publication CSV> <Output Directory>")
        sys.exit(1)
    generate_yamls(sys.argv[1], sys.argv[2], sys.argv[3])