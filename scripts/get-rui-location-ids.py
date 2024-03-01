import json
import sys

def find_rui_location_ids(json_file_path):
    """
    Searches the JSON file for `rui_location` keys and collects their `@id` values.
    
    :param json_file_path: Path to the JSON file to be searched.
    :return: A list of `@id` values.
    """
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    id_values = []

    def recursive_search(data):
        """
        Recursively searches for `rui_location` in the data and collects `@id` values.
        
        :param data: Part of the JSON data to search through.
        """
        if isinstance(data, dict):
            if 'rui_location' in data and '@id' in data['rui_location']:
                id_values.append(data['rui_location']['@id'])
            for value in data.values():
                recursive_search(value)
        elif isinstance(data, list):
            for item in data:
                recursive_search(item)
    
    recursive_search(data)

    return id_values

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py path/to/your/file.json")
        sys.exit(1)

    json_file_path = sys.argv[1]
    id_values = find_rui_location_ids(json_file_path)
    
    for id_value in id_values:
        print(id_value)