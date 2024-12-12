import csv
import os
import sys
import datetime as dt


def process_csv(file_path, column_name, county):
    entries = []

    with open(file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter='\t')
        csv_reader.fieldnames = [name.strip() for name in csv_reader.fieldnames]

        if column_name not in csv_reader.fieldnames:
            raise ValueError(f"Column '{column_name}' not found in the CSV file.")

        for row in csv_reader:
            if 'COUNTY' in row and column_name in row:
                if row['COUNTY'] == county:
                    entries.append(row[column_name].strip())

    with open(f'{county}_{column_name}.txt', mode='w', encoding='utf-8') as txt_file:
        txt_file.write("\n".join(entries))

    return entries


def sightings_per_year(file_path, column_name, county):
    entries = {}
    with open(file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter='\t')
        csv_reader.fieldnames = [name.strip() for name in csv_reader.fieldnames]

        for row in csv_reader:
            if county == 'All':
                observation_date = row['OBSERVATION DATE']
                year = observation_date.split('-')[0]

                if year in entries:
                    entries[year] += 1
                else:
                    entries[year] = 1

            elif row['COUNTY'] == county:
                observation_date = row['OBSERVATION DATE']
                year = observation_date.split('-')[0]

                if year in entries:
                    entries[year] += 1
                else:
                    entries[year] = 1
    with open(f'{county}_sightings_per_year.txt', mode='w', encoding='utf-8') as txt_file:
        for year, count in entries.items():
            txt_file.write(f"{year}: {count}\n")


def sightings_per_date(file_path):
    entries = {}
    with open(file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter='\t')
        csv_reader.fieldnames = [name.strip() for name in csv_reader.fieldnames]

        for row in csv_reader:
            observation_date = row['OBSERVATION DATE']
            year, month, day = observation_date.split('-')
            date = dt.date(int(year), int(month), int(day))
            if date in entries:
                entries[date] += 1
            else:
                entries[date] = 1
    # with open(f'{county}_sightings_per_year.txt', mode='w', encoding='utf-8') as txt_file:
    #     for year, count in entries.items():
    #         txt_file.write(f"{year}: {count}\n")
    sorted_dates = dict(sorted(entries.items()))
    return sorted_dates

file_path = 'data/ebd_US-CA_200805_200809_relOct-2024.txt'
column_name = 'COMMON NAME'
state = 'WV'
county = 'All'
if len(sys.argv) > 1:
    county = sys.argv[1]

# process_csv(file_path, column_name, county)
# sightings_per_year(file_path, column_name, county)
# sightings_per_date(file_path)
