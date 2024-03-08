import os
import json
import csv
import yaml
import argparse

def search_files(directory, doi_file):
    found_dois = []
    with open(doi_file, 'r') as f:
        doilist = [line.strip() for line in f.readlines()]
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.json', '.yaml', '.yml', '.csv')):
                file_path = os.path.join(root, file)
                if file.endswith(('.json', '.yaml', '.yml')):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        try:
                            if file.endswith('.json'):
                                content = json.load(f)
                            else:
                                content = yaml.safe_load(f)

                            content_str = json.dumps(content)
                            for doi in doilist:
                                if doi in content_str:
                                    found_dois.append(doi)
                        except Exception as e:
                            print(f"Error reading {file_path}: {e}")
                elif file.endswith('.csv'):
                    with open(file_path, newline='', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        for row in reader:
                            row_str = ','.join(row)
                            for doi in doilist:
                                if doi in row_str:
                                    found_dois.append(doi)
    return list(set(found_dois))

def main():
    parser = argparse.ArgumentParser(description='Search for DOIs in files within a directory.')
    parser.add_argument('directory', type=str, help='Directory path to search')
    parser.add_argument('doi_file', type=str, help='Path to the text file containing DOIs, one per line')
    args = parser.parse_args()

    marked_dois = search_files(args.directory, args.doi_file)
    print("Marked DOIs found in files:", marked_dois)

if __name__ == "__main__":
    main()