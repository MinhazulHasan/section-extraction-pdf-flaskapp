import pdfplumber
import io
from typing import Dict
import pandas as pd
import os


def get_the_required_table(pdf_contents: bytes) -> pd.DataFrame:
    pdf_stream = io.BytesIO(pdf_contents)
    expected_df = pd.DataFrame()

    with pdfplumber.open(pdf_stream) as pdf:
        for i, page in enumerate(pdf.pages):
            # Extract tables from the page
            tables = page.extract_tables()

            # Iterate through the tables
            for j, table in enumerate(tables):
                # Convert the table to a DataFrame
                df = pd.DataFrame(table[1:], columns=table[0])
                
                # Check if the DataFrame is not empty
                if not df.empty:
                    # Check if the first row first column contains the text "Entry costs"
                    if df.head(1).apply(lambda row: row.str.contains("Entry costs", case=False, na=False).any(), axis=1).values[0]:
                        # keep the df to expected_df
                        expected_df = df
                        break
    return expected_df



def save_table_as_csv(table_df: pd.DataFrame, file_name: str) -> None:
    os.makedirs('output_tables', exist_ok=True)
    table_csv_path = os.path.join('output_tables', f"{file_name.replace('.pdf', '.csv')}")
    table_df.to_csv(table_csv_path, index=False)



def extract_pdf_tables(pdf_contents: bytes, file_name: str) -> Dict[str, str]:
    table_df = get_the_required_table(pdf_contents)
    save_table_as_csv(table_df, file_name)
    table_dict = table_df.to_dict(orient='split')

    # Map cost category descriptions to the required JSON keys
    json_response = {
        "PRIIPsKIDEntryCostDescription": None,
        "PRIIPsKIDExitCostDescription": None,
        "PRIIPsKIDOngoingCostsDescription": None,
        "PRIIPsKIDTransactionCostsDescription": None,
        "PRIIPsKIDPerformanceFeesDescription": None
    }

    # Mapping of categories to keys
    category_key_map = {
        "Entry costs": "PRIIPsKIDEntryCostDescription",
        "Exit costs": "PRIIPsKIDExitCostDescription",
        "Management fees and other administrative or operating costs": "PRIIPsKIDOngoingCostsDescription",
        "Transaction costs": "PRIIPsKIDTransactionCostsDescription",
        "Performance fees": "PRIIPsKIDPerformanceFeesDescription"
    }

    # Iterate through each element
    for item in table_dict["data"]:
        # Ensure each item is a list with at least two elements
        if isinstance(item, list) and len(item) >= 2:
            category = item[0]
            category = ' '.join(line.strip() for line in category.splitlines())

            description = item[1]
            # Get the corresponding key from the category_key_map
            key = category_key_map.get(category)
            # Update json_response if the key exists in the map
            if key:
                json_response[key] = description

    return dict(json_response)