import pandas as pd
import argparse
import json
import os

def process_spreadsheet(csv_file, folder):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_file)
    
    # Check if 'RUI JSON ID' and 'HRA organ' columns exist
    if 'RUI JSON ID' not in df.columns or 'HRA organ' not in df.columns:
        raise ValueError("Columns 'RUI JSON ID' and 'HRA Organ' not found in the CSV file.")
    
    # Filter unique RUI JSON IDs and create JSON files
    unique_ids = df['RUI JSON ID'].unique()
    for idx, unique_id in enumerate(unique_ids, start=1):
        # Get the corresponding 'HRA Organ' value
        hra_organ = df.loc[df['RUI JSON ID'] == unique_id, 'HRA organ'].iloc[0]
        
        # Save JSON file with unique ID and 'HRA Organ' value in the name
        json_content = unique_id
        json_filename = f"{hra_organ}_{idx}.json"
        json_path = os.path.join(folder, json_filename)
        with open(json_path, 'w') as json_file:
            json_file.write(json_content)
        
        # Update all corresponding rows with JSON file names
        df.loc[df['RUI JSON ID'] == unique_id, 'RUI JSON ID'] = json_filename
    
    # Save the modified CSV file
    df.to_csv(csv_file, index=False)

def main():
    parser = argparse.ArgumentParser(description='Process CSV file and create JSON files')
    parser.add_argument('csv_file', type=str, help='Path to the CSV file')
    parser.add_argument('folder', type=str, help='Folder to store JSON files')
    args = parser.parse_args()
    
    process_spreadsheet(args.csv_file, args.folder)

if __name__ == '__main__':
    main()