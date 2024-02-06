import yaml
import sys

def comment_age(data):
    """
    Recursively search through the data to find and comment out the 'Age' key.
    This function modifies the structure to include a comment indicator for 'Age' keys.
    """
    if isinstance(data, dict):
        for key in list(data.keys()):
            if key == 'age':
                # Prefixing the key with a comment indicator
                data[f'# {key} (commented out)'] = data.pop(key)
            else:
                data[key] = comment_age(data[key])
    elif isinstance(data, list):
        for i in range(len(data)):
            data[i] = comment_age(data[i])
    return data

def process_yaml_file(file_path):
    """
    Reads a YAML file, comments out 'age' properties, and overwrites the file with the modified content.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        
        # Process the YAML data to comment out 'age'
        modified_data = comment_age(data)

        # Overwrite the original YAML file with the modified data
        with open(file_path, 'w', encoding='utf-8') as file:
            yaml.dump(modified_data, file, default_flow_style=False, sort_keys=False)
        
        print(f"File {file_path} has been processed and overwritten with the modified content.")
    
    except Exception as e:
        print(f"Error processing the file: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_yaml_file>")
    else:
        file_path = sys.argv[1]
        process_yaml_file(file_path)