import glob
import pandas as pd

def csv_to_excel(csv_files, output_excel):
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    excel_writer = pd.ExcelWriter(output_excel, engine='xlsxwriter')

    # Loop through each CSV file and convert it to a worksheet in the Excel file.
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        sheet_name = csv_file.split('/')[0][:31]  # Extract sheet name from CSV file name
        df.to_excel(excel_writer, sheet_name=sheet_name, index=False)

    # Close the Pandas Excel writer and save the Excel file.
    excel_writer.close()

if __name__ == "__main__":
    # Use glob to find all CSV files in the directory
    input_csv_files = glob.glob("*/*.csv")

    # Output Excel file
    output_excel_file = "output.xlsx"  # Update with your desired output file name

    # Call the function to convert CSVs to Excel
    csv_to_excel(input_csv_files, output_excel_file)
