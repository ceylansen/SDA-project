import csv
import os


# Extracts specific columns from file and writes to document
def extract_column_entries(file_path):
    """
    Reads a CSV file and extracts all entries from a specified column.

    Parameters:
        file_path (str): The path to the CSV file.
        column_name (str): The name of the column to extract.

    Returns:
        list: A list containing all entries from the specified column.
    """
    column_name = 'Common_Name'
    area_code = 'DEWA'
    entries = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            if column_name not in csv_reader.fieldnames:
                raise ValueError(f"Column '{column_name}' not found in the CSV file.")
            for row in csv_reader:
                if row['\ufeffUnit_Code'] == area_code:
                    entries.append(row[column_name])

            with open(f'{area_code}{column_name}.txt', mode='w', encoding='utf-8') as txt_file:
                txt_file.write("\n".join(entries))

            return entries

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []


# Counts sightings per unit code
def count_sightings_perArea_perYear(file_path):
    area_code = 'DEWA'
    entries = {}
    try:
        with open(file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if row['\ufeffUnit_Code'] == area_code:
                    if entries.get(row['Year'], False) != False:
                        entries[row['Year']] += 1
                    else:
                        entries[row['Year']] = 1
            print(entries)
            with open(f'{area_code}sightingPerYear.txt', mode='w', encoding='utf-8') as txt_file:
                txt_file.write("\n".join(entries))

            return entries

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []


# Counts unique entries
def count_unique_entries(text_file):
    with open(text_file, mode='r', encoding='utf-8') as file:
        lines = file.readlines()
        entries = [line.strip() for line in lines]
        unique_counts = {}
        for entry in entries:
            if entry in unique_counts:
                unique_counts[entry] += 1
            else:
                unique_counts[entry] = 1

        return unique_counts

