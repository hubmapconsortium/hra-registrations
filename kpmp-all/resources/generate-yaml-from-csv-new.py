import pandas as pd
import yaml
import os
import uuid
import sys

def generate_yaml(kpmp_csv_path):
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

    # Read the CSV file into a DataFrame
    kpmp_csv = pd.read_csv(kpmp_csv_path)
    
    yaml_content = [
        {
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
    ]
        
    
    for _, pub_row in kpmp_csv.iterrows():
        rui_location = get_rui_location(pub_row["Sex"], pub_row["Location"], pub_row["Laterality"])
        # put this in a conditional that checks whether the donor ID exists already
        donor = {
            "sex": pub_row["Sex"],
            "label": pub_row["Participant ID"] + ", " + pub_row["Age (Years) (Binned)"],
            "link": pub_row["KPMP Atlas Repository Link"],
        }
        yaml_content[0]["donors"].append(donor)
        # assign "rui_location" variable above to the rui_location property of the sample under the donor
        # "rui_location": rui_location
        # then create the dataset array and add id, link, and technology
        
        

    # Create the YAML file in the current working directory
    current_directory = os.getcwd()
    filename = "registrations.yaml"
    filepath = os.path.join(current_directory, filename)
    
    # Write the YAML content with the desired format
    with open(filepath, 'w') as file:
        file.write("# yaml-language-server: $schema=https://raw.githubusercontent.com/hubmapconsortium/hra-rui-locations-processor/main/registrations.schema.json\n\n")
        yaml.dump(yaml_content, file, allow_unicode=True, sort_keys=False, default_flow_style=False)

    print(f"YAML file created at: {filepath}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_yaml.py <CSV>")
        sys.exit(1)
    generate_yaml(sys.argv[1])
