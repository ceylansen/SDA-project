import sqlite3
import csv
import math
from collections import Counter
import matplotlib.pyplot as plt
import sys

def shannon_index_sightings(file_path):
    species_counts = Counter()

    with open(file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter='\t')
        csv_reader.fieldnames = [name.strip() for name in csv_reader.fieldnames]

        for row in csv_reader:
            common_name = row["COMMON NAME"].strip()
            species_counts[common_name] += 1

    total_sightings = sum(species_counts.values())

    shannon_index = 0
    for count in species_counts.values():
        p_i = count / total_sightings
        shannon_index -= p_i * math.log(p_i)
    return shannon_index

def shannon_index_by_month(file_path, month, year):
    species_counts = Counter()

    with open(file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter='\t')
        csv_reader.fieldnames = [name.strip() for name in csv_reader.fieldnames]

        for row in csv_reader:
            date = row["OBSERVATION DATE"]
            y, m, d = date.split('-')
            if year == int(y) and month == int(m):
                common_name = row["COMMON NAME"].strip()
                species_counts[common_name] += 1
            elif int(y) > year:
                break

    total_sightings = sum(species_counts.values())
    shannon_index = 0
    for count in species_counts.values():
        p_i = count / total_sightings
        shannon_index -= p_i * math.log(p_i)
    return shannon_index


file_path = 'data/ebd_2006_2015.txt'
column_name = 'COMMON NAME'
state = 'CA'
county = 'All'
db_path = 'data/firedata.sqlite'
if len(sys.argv) > 1:
    county = sys.argv[1]

# print(shannon_index_sightings(file_path))
# print(shannon_index_by_month(file_path, 1, 2006))
# print(shannon_index_by_month(file_path, 2, 2006))
# print(shannon_index_by_month(file_path, 3, 2006))
# print(shannon_index_by_month(file_path, 4, 2006))