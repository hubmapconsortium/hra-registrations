#!/usr/bin/env python3
"""
Extract individual RUI locations from a rui_locations.jsonld file.

Usage:
    python extract_rui_locations.py <input_file> [output_folder]

Example:
    python extract_rui_locations.py hubmap-pancreas_millitome-saunders-2024/rui_locations.jsonld output
"""

import json
import os
import sys
from pathlib import Path


def extract_hubmap_id(link):
    """Extract HuBMAP ID from the portal link."""
    # Link format: https://portal.hubmapconsortium.org/browse/HBM625.ZFTZ.894
    return link.split('/')[-1]


def process_rui_locations(input_file, output_folder):
    """Process the rui_locations.jsonld file and create individual JSON files."""
    
    # Read the input file
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Create output folder if it doesn't exist
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Process each donor in the @graph
    count = 0
    for node in data.get('@graph', []):
        if node.get('@type') == 'Donor':
            samples = node.get('samples', [])
            
            for sample in samples:
                # Check if sample has a rui_location
                if 'rui_location' not in sample:
                    continue
                
                # Extract HuBMAP ID from the link
                link = sample.get('link', '')
                if not link:
                    print(f"Warning: Sample {sample.get('label', 'unknown')} has no link, skipping")
                    continue
                
                hubmap_id = extract_hubmap_id(link)
                
                # Get the rui_location content
                rui_location = sample['rui_location']
                
                # Write to file
                output_file = output_path / f"{hubmap_id}.json"
                with open(output_file, 'w') as f:
                    json.dump(rui_location, f, indent=2)
                
                count += 1
                print(f"Created: {output_file}")
    
    print(f"\nTotal files created: {count}")
    return count


def main():
    if len(sys.argv) < 2:
        print("Error: Input file required")
        print(__doc__)
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Default output folder is based on input file name
    if len(sys.argv) >= 3:
        output_folder = sys.argv[2]
    else:
        # Create output folder next to input file
        input_path = Path(input_file)
        output_folder = input_path.parent / "rui_locations_output"
    
    # Validate input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    print(f"Processing: {input_file}")
    print(f"Output folder: {output_folder}")
    print("-" * 60)
    
    process_rui_locations(input_file, output_folder)


if __name__ == '__main__':
    main()
