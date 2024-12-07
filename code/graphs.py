import sqlite3
import csv
import math
from collections import Counter
import matplotlib.pyplot as plt
import sys

def extract_fires(state, year1, year2):
    db_path = 'data/FPA_FOD_20170508.sqlite'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    fires = {}
    cursor.execute(
        f"""
        SELECT DISCOVERY_DATE, FIRE_SIZE
        FROM Fires
        WHERE STATE = '{state}'
        AND FIRE_YEAR BETWEEN {year1} AND {year2};
        """
        )
    rows = cursor.fetchall()
    biggest_fire = 0
    for row in rows:
        if fires.get(row[0], False) == False:
            fires[row[0]] = row[1]
        else:
            fires[row[0]] += row[1]
        if biggest_fire < row[1]:
            biggest_fire = row[1]
    conn.close()
    sorted_fires = dict(sorted(fires.items()))
    return sorted_fires

def shannon_index_sightings(file_path):
    species_counts = Counter()

    # Read the dataset
    with open(file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter='\t')
        csv_reader.fieldnames = [name.strip() for name in csv_reader.fieldnames]

        # Count occurrences of each species
        for row in csv_reader:
            common_name = row["COMMON NAME"].strip()
            species_counts[common_name] += 1

    # Total number of sightings
    total_sightings = sum(species_counts.values())

    # Calculate Shannon index
    shannon_index = 0
    for count in species_counts.values():
        p_i = count / total_sightings  # Proportion of species i
        shannon_index -= p_i * math.log(p_i)  # Add to the Shannon index

    return shannon_index

def sightings_ebird(file_path, column_name, county):
    entries = {}
    with open(file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter='\t')
        csv_reader.fieldnames = [name.strip() for name in csv_reader.fieldnames]

        for row in csv_reader:
            observation_date = row['OBSERVATION DATE']
            if entries.get(observation_date, False) == False:
                entries[observation_date] = 1
            else:
                entries[observation_date] += 1
    # print(entries)
    return entries
    # with open(f'{county}_sightings_per_year.txt', mode='w', encoding='utf-8') as txt_file:
    #     for year, count in entries.items():
    #         txt_file.write(f"{year}: {count}\n")

file_path = 'data/ebd_US-CA_200805_200809_relOct-2024.txt'
column_name = 'COMMON NAME'
state = 'WV'
county = 'All'
if len(sys.argv) > 1:
    county = sys.argv[1]

# process_csv(file_path, column_name, county)
# sightings = sightings_ebird(file_path, column_name, county)
print(shannon_index_sightings(file_path))