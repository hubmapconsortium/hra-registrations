#!/usr/bin/env python3

import sys
import yaml

def find_link_value(node):
    """Recursively search for the 'link' property in the YAML data."""
    if isinstance(node, dict):
        if 'link' in node:
            return node['link']
        for key, value in node.items():
            result = find_link_value(value)
            if result:
                return result
    elif isinstance(node, list):
        for item in node:
            result = find_link_value(item)
            if result:
                return result
    return None

def update_node(node, link_value, first_id=[True]):
    if isinstance(node, dict):
        if 'id' in node:
            if first_id[0]:
                node['id'] = link_value
                first_id[0] = False
            else:
                node['id'] = f"{link_value}#{node['id']}"
        if 'rui_location' in node:
            node['datasets'] = [{'technology': 'OTHER'}]
        for value in node.values():
            update_node(value, link_value, first_id)
    elif isinstance(node, list):
        for item in node:
            update_node(item, link_value, first_id)

def update_yaml_file(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    # Find the link value from the YAML data
    link_value = find_link_value(data)
    if not link_value:
        print("No 'link' property found in the YAML data.")
        return

    # Update the YAML data with the found link_value
    update_node(data, link_value)

    with open(file_path, 'w') as file:
        yaml.safe_dump(data, file, default_flow_style=False, sort_keys=False)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python update_yaml.py path/to/your/file.yaml")
    else:
        file_path = sys.argv[1]
        update_yaml_file(file_path)
        print(f"YAML file '{file_path}' has been updated.")