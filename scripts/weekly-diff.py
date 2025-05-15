import os
import yaml
import gspread
from datetime import date
from oauth2client.service_account import ServiceAccountCredentials

# ---- CONFIGURATION ----
GITHUB_REPO_PATH = "../"  # 🔁 Replace this with your local repo path
REGISTRATION_FILENAME = "registrations.yaml"
GOOGLE_SHEET_NAME = "RUI Dashboard"
GOOGLE_CREDENTIALS_FILE = "/Users/dequeue/Desktop/RUI.nosync/hra1231-c39c9597adfb.json"

# ---- Step 1: Count donors, samples, blocks, datasets ----
def count_all_entities():
    donor_count = 0
    sample_count = 0
    section_count = 0
    dataset_count = 0

    for root, dirs, files in os.walk(GITHUB_REPO_PATH):
        for file in files:
            if file == REGISTRATION_FILENAME:
                file_path = os.path.join(root, file)
                print(f"Parsing: {file_path}")
                with open(file_path, 'r') as f:
                    try:
                        data = yaml.safe_load(f)
                        if not isinstance(data, list):
                            print("  ⚠️ Unexpected structure: not a list.")
                            continue

                        for entry in data:
                            donors = entry.get("donors", [])
                            donor_count += len(donors)

                            for donor in donors:
                                samples = donor.get("samples", [])
                                sample_count += len(samples)

                                for sample in samples:
                                    # Count datasets directly under sample
                                    sample_datasets = sample.get("datasets", [])
                                    dataset_count += len(sample_datasets)

                                    sections = sample.get("sections", [])
                                    section_count += len(sections)

                                    for section in sections:
                                        section_datasets = section.get("datasets", [])
                                        dataset_count += len(section_datasets)
                    except Exception as e:
                        print(f"Error parsing {file_path}: {e}")

    print(f"\nFinal Counts:")
    print(f"  Donors:   {donor_count}")
    print(f"  Samples:  {sample_count}")
    print(f"  Sections: {section_count}")
    print(f"  Datasets: {dataset_count}")
    return donor_count, sample_count, section_count, dataset_count

# ---- Step 2: Write to Google Sheet ----
def write_to_google_sheet(date_str, donors, samples, blocks, datasets):
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive'
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)

    sheet = client.open(GOOGLE_SHEET_NAME).worksheet("GitHuB Tracker")

    # Get header row (dates)
    header = sheet.row_values(1)

    if date_str in header:
        print(f"Date {date_str} already exists — skipping insert.")
        return

    # Insert new column at position 2 (second column)
    sheet.insert_cols([[""]], col=2)  # shift existing columns to the right

    # Set new date header
    sheet.update_cell(1, 2, date_str)

    # Set metric values
    values = [donors, samples, sections, datasets]
    for i, val in enumerate(values):
        sheet.update_cell(i + 2, 2, val)

    print(f"Inserted new column for {date_str} at position 2.")

# ---- Run all steps ----
if __name__ == "__main__":
    today = date.today().isoformat()
    donors, samples, sections, datasets = count_all_entities()
    write_to_google_sheet(today, donors, samples, sections, datasets)