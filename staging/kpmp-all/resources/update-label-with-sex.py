import argparse
import yaml

def update_donor_labels(file_path):
    # Load the YAML file
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    # Iterate through the top-level entries
    for entry in data:
        # Check if the entry contains the 'donors' key
        if 'donors' in entry:
            # Iterate through each donor in the 'donors' list
            for donor in entry['donors']:
                # Check if 'sex' and 'label' are in the donor's data
                if 'sex' in donor and 'label' in donor:
                    # Update the 'label' property
                    donor['label'] = donor['sex'] + ", " + donor['label']

    # Write the updated data back to the file
    with open(file_path, 'w') as file:
        yaml.safe_dump(data, file, default_flow_style=False, allow_unicode=True)

def main():
    parser = argparse.ArgumentParser(description="Update donor labels in a YAML file.")
    parser.add_argument('file_path', type=str, help="The path to the YAML file to be processed")

    args = parser.parse_args()

    # Update the donor labels in the specified YAML file
    update_donor_labels(args.file_path)

if __name__ == "__main__":
    main()