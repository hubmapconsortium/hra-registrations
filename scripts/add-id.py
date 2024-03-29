import sys
import yaml

def update_yaml(filename):
    # Read the YAML file
    with open(filename, 'r') as file:
        data = yaml.safe_load(file)

    # Iterate through each donor and update the label
    for donor in data[0]['donors']:
        donor_id = donor['id'].split('#')[1]
        donor['label'] = f"{donor_id}, {donor['label']}"

    # Write the updated YAML back to the file
    with open(filename, 'w') as file:
        yaml.dump(data, file)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py filename.yaml")
        sys.exit(1)

    filename = sys.argv[1]
    update_yaml(filename)