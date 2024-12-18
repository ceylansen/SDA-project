import pandas as pd


# Extracts entries from excel file
def extract_entries_from_excel(file_path, sheet_name=None):
    """
    Extracts entries from an Excel file and returns the data as a DataFrame.

    :param file_path: str - The path to the Excel file (.xlsx).
    :param sheet_name: str or None - The name of the sheet to read. Default is None (reads the first sheet).
    :return: pd.DataFrame - The extracted data.
    """
    try:
        if sheet_name:
            data = pd.read_excel(file_path, sheet_name=sheet_name)
        else:
            data = pd.read_excel(file_path)  # Defaults to the first sheet

        return data
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

