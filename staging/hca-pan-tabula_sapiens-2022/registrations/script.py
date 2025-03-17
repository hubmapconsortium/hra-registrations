import os
import json

def update_json_files(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):  # Process only JSON files
            file_path = os.path.join(folder_path, filename)
            
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Update creator fields
            data["creator"] = "Heidi Schlehlein"
            data["creator_first_name"] = "Heidi"
            data["creator_last_name"] = "Schlehlein"
            
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2)  # Pretty-print with 2-space indentation
            
            print(f"Updated: {filename}")

# Example usage
folder_path = "."  # Replace with your actual folder path
update_json_files(folder_path)