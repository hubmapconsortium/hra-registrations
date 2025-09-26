#!/usr/bin/env python3
"""
RUI Registration Daily Tracker - HuBMAP & SenNet Combined Analysis

This script tracks RUI location registration coverage for both HuBMAP and SenNet datasets over time.
It generates daily counts for:
- Total datasets
- Supported datasets (in organs covered by reference anatomy)
- Registered datasets (with RUI locations)

Results are saved to a CSV file with dates as columns and metrics as rows for time-series analysis.
"""

import requests
import re
import csv
import os
import sys
from datetime import datetime
from collections import Counter
import getpass
import pandas as pd
import cellxgene_census

def get_api_tokens():
    """Prompt user for API tokens"""
    print("=" * 60)
    print("RUI Registration Daily Tracker")
    print("=" * 60)
    print("Please provide your API tokens:")
    print()
    
    hubmap_token = getpass.getpass("HuBMAP API Token: ")
    sennet_token = getpass.getpass("SenNet API Token: ")
    
    if not hubmap_token.strip():
        print("Warning: No HuBMAP token provided")
    if not sennet_token.strip():
        print("Warning: No SenNet token provided")
    
    return hubmap_token.strip(), sennet_token.strip()

def setup_configuration(hubmap_token, sennet_token):
    """Setup API endpoints and configuration"""
    config = {
        'hubmap_token': hubmap_token,
        'sennet_token': sennet_token,
        'hubmap_api_url': "https://search.api.hubmapconsortium.org/v3/search",
        'sennet_api_url': "https://search.api.sennetconsortium.org/search",
        'reference_organs_url': "https://apps.humanatlas.io/api/v1/reference-organs",
        'hubmap_headers': {"Authorization": f"Bearer {hubmap_token}"},
        'sennet_headers': {"Authorization": f"Bearer {sennet_token}"},
        'csv_output_path': "../combined_weekly_counts.csv",
        'metadata_path': "./RUI Reporter/metadata.js"
    }
    
    print(f"Configuration setup complete:")
    print(f"  HuBMAP API: {config['hubmap_api_url']}")
    print(f"  SenNet API: {config['sennet_api_url']}")
    print(f"  Output CSV: {config['csv_output_path']}")
    print()
    
    return config

def extract_organ_mappings(metadata_path):
    """Extract code_to_uberon mapping from metadata.js"""
    code_to_uberon = {}
    
    try:
        with open(metadata_path, "r") as f:
            content = f.read()
            # Parse the organ mappings using regex
            matches = re.findall(r"(\w+):\s*{\s*code: '(\w+)',\s*label: '[^']+',\s*organ_id: '([^']+)'", content)
            for code, _, uberon in matches:
                code_to_uberon[code] = uberon
        
        print(f"Successfully extracted {len(code_to_uberon)} organ code mappings")
        
    except FileNotFoundError:
        print(f"Warning: metadata.js file not found at {metadata_path}")
        print("Using empty mapping - this may result in no supported datasets")
    except Exception as e:
        print(f"Error parsing metadata.js: {e}")
    
    return code_to_uberon

def filter_by_organ_metadata_cellxgene(df: pd.DataFrame, metadata_path: str) -> pd.DataFrame:
    """
    Reads a metadata.js file and keeps only rows in the DataFrame
    where tissue_general_ontology_term_id matches one of the organ_id entries.
    
    Args:
        df: pandas DataFrame containing a column 'tissue_general_ontology_term_id'
        metadata_path: path to the metadata.js file
    
    Returns:
        Filtered pandas DataFrame
    """
    organ_ids = set()
    
    try:
        with open(metadata_path, "r") as f:
            content = f.read()
            # Extract all organ_id values using regex
            matches = re.findall(r"organ_id:\s*'([^']+)'", content)
            organ_ids.update(matches)
        
        print(f"Extracted {len(organ_ids)} organ IDs from {metadata_path}")
    
    except FileNotFoundError:
        print(f"Warning: metadata.js file not found at {metadata_path}")
        print("No filtering will be applied.")
        return df
    except Exception as e:
        print(f"Error parsing metadata.js: {e}")
        return df

    # Filter DataFrame
    filtered_df = df[df["tissue_general_ontology_term_id"].isin(organ_ids)].copy()
    # print(f"Filtered DataFrame to {len(filtered_df)} rows matching organ IDs")
    
    return filtered_df

def call_cellxgene_api(metadata_path):
        with cellxgene_census.open_soma(census_version="2025-01-30") as census:
            # Read the obs DataFrame
            cell_metadata = census["census_data"]["homo_sapiens"].obs.read(
                column_names = ['dataset_id','tissue_general_ontology_term_id'
                ]
            )
            cell_metadata = cell_metadata.concat().to_pandas()

        unique_df = cell_metadata[["dataset_id", "tissue_general_ontology_term_id"]].drop_duplicates() 
        cellxgene_counts = len(unique_df) #total count
        print(f"Total unique rows after removing duplicates: {len(unique_df)}")

        # Filter using metadata.js organ mapping
        filtered_df = filter_by_organ_metadata_cellxgene(unique_df, metadata_path)

        cellxgene_supported_counts = len(filtered_df) #supported counts

        return [cellxgene_counts, cellxgene_supported_counts]


def iri_to_curie(iri):
    """Convert UBERON IRI to CURIE format (e.g., UBERON:0001234)"""
    if iri and "obo/UBERON_" in iri:
        return "UBERON:" + iri.split("_")[-1]
    return iri

def fetch_reference_organs(reference_organs_url):
    """Fetch all reference organs from HRA API"""
    try:
        response = requests.get(reference_organs_url)
        response.raise_for_status()
        organs = response.json()
        
        # Extract and normalize UBERON IDs
        reference_uberon_ids = {
            iri_to_curie(organ.get("representation_of")) 
            for organ in organs 
            if organ.get("representation_of")
        }
        
        print(f"Successfully fetched {len(organs)} reference organs")
        print(f"Extracted {len(reference_uberon_ids)} unique UBERON IDs")
        
        return reference_uberon_ids
        
    except requests.RequestException as e:
        print(f"Error fetching reference organs: {e}")
        return set()
    except Exception as e:
        print(f"Unexpected error: {e}")
        return set()

def filter_supported_codes(code_to_uberon, reference_uberon_ids):
    """Filter organ codes to only those whose UBERON IDs are in the reference set"""
    filtered_supported_codes = [
        code for code, uberon in code_to_uberon.items() 
        if uberon in reference_uberon_ids
    ]
    
    print(f"Total organ codes in metadata: {len(code_to_uberon)}")
    print(f"Supported organ codes (in reference anatomy): {len(filtered_supported_codes)}")
    
    return filtered_supported_codes

def query_consortium_datasets(api_url, headers, filtered_supported_codes, consortium_name):
    """Query API for dataset counts"""
    
    if consortium_name == "HuBMAP":
        # HuBMAP queries (existing working queries)
        # 1. Total count of all datasets
        total_query = {
            "query": {
                "bool": {
                    "filter": [
                        {"match": {"entity_type.keyword": "Dataset"}}
                    ]
                }
            },
            "size": 0
        }
        
        # 2. Count of datasets where organ matches supported codes
        supported_query = {
            "query": {
                "bool": {
                    "filter": [
                        {"match": {"entity_type.keyword": "Dataset"}},
                        {"terms": {"origin_samples.organ.keyword": filtered_supported_codes}},
                        {"match": {"origin_samples.sample_category.keyword": "organ"}}
                    ]
                }
            },
            "size": 0
        }
        
        # 3. Count of datasets with organ in supported codes AND rui_location present
        registered_query = {
            "query": {
                "bool": {
                    "filter": [
                        {"match": {"entity_type.keyword": "Dataset"}},
                        {"terms": {"origin_samples.organ.keyword": filtered_supported_codes}},
                        {"match": {"origin_samples.sample_category.keyword": "organ"}},
                        {"exists": {"field": "ancestors.rui_location"}}
                    ]
                }
            },
            "size": 0
        }
        
    else:  # SenNet
        # SenNet queries (copied from working notebook)
        # 1. Total count of all datasets
        total_query = {
            "version": True,
            "size": 0,
            "track_total_hits": True,
            "query": {
                "bool": {
                    "filter": [
                        {"term": {"entity_type.keyword": "Dataset"}},
                        {"term": {"creation_action.keyword": "Create Dataset Activity"}}
                    ]
                }
            }
        }
        
        # 2. Count of supported datasets (with or without RUI information)
        supported_query = {
            "query": {
                "bool": {
                    "filter": [
                        {
                            "terms": {
                                "entity_type.keyword": [
                                    "Dataset"
                                ]
                            }
                        },
                        {
                            "terms": {
                                "creation_action.keyword": [
                                    "Create Dataset Activity"
                                ]
                            }
                        },
                        {
                            "terms": {
                                "has_rui_information.keyword": [
                                    "True",
                                    "False"
                                ]
                            }
                        }
                    ]
                }
            },
            "from": 0,
            "size": 0,
            "track_total_hits": True
        }
        
        # 3. Count of registered datasets (with RUI information)
        registered_query = {
            "query": {
                "bool": {
                    "filter": [
                        {
                            "terms": {
                                "entity_type.keyword": [
                                    "Dataset"
                                ]
                            }
                        },
                        {
                            "terms": {
                                "creation_action.keyword": [
                                    "Create Dataset Activity"
                                ]
                            }
                        },
                        {
                            "terms": {
                                "has_rui_information.keyword": [
                                    "True"
                                ]
                            }
                        }
                    ]
                }
            },
            "from": 0,
            "size": 0,
            "track_total_hits": True
        }
    
    try:
        # Execute queries
        total_resp = requests.post(api_url, json=total_query, headers=headers)
        supported_resp = requests.post(api_url, json=supported_query, headers=headers)
        registered_resp = requests.post(api_url, json=registered_query, headers=headers)
        
        # Check for API errors
        total_resp.raise_for_status()
        supported_resp.raise_for_status()
        registered_resp.raise_for_status()
        
        # Extract counts
        total_count = total_resp.json()['hits']['total']['value']
        supported_count = supported_resp.json()['hits']['total']['value']
        registered_count = registered_resp.json()['hits']['total']['value']
        
        print(f"{consortium_name} Dataset Counts:")
        print(f"  Total datasets: {total_count}")
        print(f"  Supported datasets: {supported_count}")
        print(f"  Registered datasets: {registered_count}")
        
        return total_count, supported_count, registered_count
        
    except requests.RequestException as e:
        print(f"Error querying {consortium_name} API: {e}")
        return 0, 0, 0
    except Exception as e:
        print(f"Unexpected error querying {consortium_name}: {e}")
        return 0, 0, 0

def write_counts_to_csv(csv_output_path, hubmap_counts, sennet_counts, cellxgene_counts):
    """Write the collected counts to CSV with dates as columns"""
    
    # Get current timestamp for column header
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Prepare data: each row is a metric, each column is a date
    new_data = {
        'HuBMAP Total Datasets': hubmap_counts[0],
        'HuBMAP Supported Datasets': hubmap_counts[1], 
        'HuBMAP Registered Datasets': hubmap_counts[2],
        'SenNet Total Datasets': sennet_counts[0],
        'SenNet Supported Datasets': sennet_counts[1],
        'SenNet Registered Datasets': sennet_counts[2],
        'CellXGene Total Datasets': cellxgene_counts[0],
        'CellXGene Supported Datasets':cellxgene_counts[1]
    }
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(csv_output_path), exist_ok=True)
    
    # Check if CSV file exists
    file_exists = os.path.isfile(csv_output_path)
    
    if not file_exists:
        # Create new CSV file with headers and first data column
        with open(csv_output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header row with metric names and first date
            header = ['Metric'] + [current_date]
            writer.writerow(header)
            
            # Write data rows
            for metric, value in new_data.items():
                writer.writerow([metric, value])
        
        print(f"Created new CSV file: {csv_output_path}")
        
    else:
        # Read existing CSV and add new column
        with open(csv_output_path, 'r', newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        if len(rows) == 0:
            # Empty file, treat as new
            rows = [['Metric'], ['HuBMAP Total Datasets'], ['HuBMAP Supported Datasets'], 
                   ['HuBMAP Registered Datasets'], ['SenNet Total Datasets'], 
                   ['SenNet Supported Datasets'], ['SenNet Registered Datasets'],['CellXGene Total Datasets'],
                   ['CellXGene Supported Datasets']]
        
        # Check if today's data already exists (avoid duplicates)
        if current_date in rows[0]:
            print(f"Data for {current_date} already exists. Updating existing entry.")
            date_index = rows[0].index(current_date)
        else:
            # Add new date to header
            rows[0].append(current_date)
            date_index = len(rows[0]) - 1
        
        # Add new data to each metric row
        metric_to_row = {}
        for i, row in enumerate(rows[1:], 1):
            if len(row) > 0:
                metric_to_row[row[0]] = i
        
        # Ensure all metrics exist and add new values
        for metric, value in new_data.items():
            if metric in metric_to_row:
                row_index = metric_to_row[metric]
                # Pad row if necessary
                while len(rows[row_index]) < date_index + 1:
                    rows[row_index].append('')
                rows[row_index][date_index] = value
            else:
                # Add new metric row
                new_row = [metric] + [''] * (date_index - 1) + [value]
                rows.append(new_row)
        
        # Pad any short rows
        max_cols = len(rows[0])
        for row in rows:
            while len(row) < max_cols:
                row.append('')
        
        # Write updated CSV
        with open(csv_output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        
        print(f"Updated existing CSV file: {csv_output_path}")
    
    # Display summary
    print(f"\\nData added for {current_date}:")
    for metric, value in new_data.items():
        print(f"  {metric}: {value}")

def main():
    """Main execution function"""
    print(f"Starting RUI Registration Daily Tracker at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Get API tokens from user input
        hubmap_token, sennet_token = get_api_tokens()
        
        # Setup configuration
        config = setup_configuration(hubmap_token, sennet_token)
        
        # Extract organ mappings
        code_to_uberon = extract_organ_mappings(config['metadata_path'])
        
        # Fetch reference organs
        reference_uberon_ids = fetch_reference_organs(config['reference_organs_url'])
        
        # Filter supported codes
        filtered_supported_codes = filter_supported_codes(code_to_uberon, reference_uberon_ids)
        
        if not filtered_supported_codes:
            print("Warning: No supported organ codes found. Results may be empty.")
        
        # Query HuBMAP datasets
        print("\\nQuerying HuBMAP datasets...")
        hubmap_counts = query_consortium_datasets(
            config['hubmap_api_url'], 
            config['hubmap_headers'], 
            filtered_supported_codes, 
            "HuBMAP"
        )
        
        # Query SenNet datasets
        print("\\nQuerying SenNet datasets...")
        sennet_counts = query_consortium_datasets(
            config['sennet_api_url'], 
            config['sennet_headers'], 
            filtered_supported_codes, 
            "SenNet"
        )

        #Query CELLXGENE datasets
        print("\\nQuerying CELLXGENE datasets...")
        cell_x_gene_counts = call_cellxgene_api(config['metadata_path'])
        # Write results to CSV
        print("\\nWriting results to CSV...")
        write_counts_to_csv(config['csv_output_path'], hubmap_counts, sennet_counts,cell_x_gene_counts)
        
        print(f"\\nScript completed successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Calculate and display coverage percentages
        if hubmap_counts[1] > 0:
            hubmap_coverage = (hubmap_counts[2] / hubmap_counts[1]) * 100
            print(f"HuBMAP Registration Coverage: {hubmap_counts[2]}/{hubmap_counts[1]} = {hubmap_coverage:.1f}%")
        
        if sennet_counts[1] > 0:
            sennet_coverage = (sennet_counts[2] / sennet_counts[1]) * 100
            print(f"SenNet Registration Coverage: {sennet_counts[2]}/{sennet_counts[1]} = {sennet_coverage:.1f}%")
        
    except KeyboardInterrupt:
        print("\\nScript interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\\nError during execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()