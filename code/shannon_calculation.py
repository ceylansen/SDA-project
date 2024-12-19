import sqlite3
import numpy as np
from scipy.fft import fft, fftfreq
import csv
import math
import os
from collections import Counter
import matplotlib.pyplot as plt
import datetime as dt
import sys
from statsmodels.tsa.stattools import kpss
from statsmodels.tsa.stattools import adfuller
import os


# Filters dataset to specified years and saves necessary columns
def filter_for_county(input_file, year = list, output_dir='filtered'):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    with open(input_file, mode='r', encoding='utf-8') as csv_file:
        print("reading in file...")
        csv_reader = csv.DictReader(csv_file, delimiter='\t')
        csv_reader.fieldnames = [name.strip() for name in csv_reader.fieldnames]

        year_file_path = os.path.join(output_dir, f"filtered_for_counties.txt")

        print("writing to file")
        with open(year_file_path, 'w') as year_file:
            # Write the header to the output file
            year_file.write(f"OBSERVATION DATE\t'COMMON NAME'\t'COUNTY'\t'COUNTY CODE'\n")
            for row in csv_reader:
                if len(year) != 0:
                    date = row['OBSERVATION DATE']
                    year_entry = date.split('-')[0]
                    if int(year_entry) in year:
                        year_file.write(f"{row['OBSERVATION DATE']}\t{row['COMMON NAME']}\t{row['COUNTY']}\t{row['COUNTY CODE']}\n")
                else:
                    year_file.write(f"{row['OBSERVATION DATE']}\t{row['COMMON NAME']}\t{row['COUNTY']}\t{row['COUNTY CODE']}\n")


# Sorts given file by dates, recommended size of file = 1 year, otherwise
# it will be killed unless you have enough ram
def sort_year_by_date(input_file, output_file, date_column='OBSERVATION DATE'):
    with open(input_file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file, delimiter='\t')
        csv_reader.fieldnames = [name.strip() for name in csv_reader.fieldnames]

        if date_column not in csv_reader.fieldnames:
            raise ValueError(f"Column '{date_column}' must be present in the file.")

        # Read and sort rows by the date column
        sorted_rows = sorted(
            csv_reader,
            key=lambda row: dt.datetime.strptime(row[date_column], '%Y-%m-%d')
        )

    with open(output_file, mode='w', encoding='utf-8') as file:
        csv_writer = csv.DictWriter(file, fieldnames=csv_reader.fieldnames, delimiter='\t')
        csv_writer.writeheader()
        csv_writer.writerows(sorted_rows)


# Stored shannon index of the state California per month, this this took a while to compute
def shannon_index_by_month_CA():
    shannon_index = {dt.date(2006, 1, 15): 5.13392382109124, dt.date(2006, 2, 15): 5.113348158753306, dt.date(2006, 3, 15): 5.114262021259862, dt.date(2006, 4, 15): 5.224760883557517, dt.date(2006, 5, 15): 5.171996817626759, dt.date(2006, 6, 15): 5.136022591043768, dt.date(2006, 7, 15): 5.237388261032557, dt.date(2006, 8, 15): 5.283679535122384, dt.date(2006, 9, 15): 5.312001380553248, dt.date(2006, 10, 15): 5.2334501636047115, dt.date(2006, 11, 15): 5.1513741347162565, dt.date(2006, 12, 15): 5.143742602095986, dt.date(2007, 1, 15): 5.129459973668558, dt.date(2007, 2, 15): 5.093402547566193, dt.date(2007, 3, 15): 5.107668262537926, dt.date(2007, 4, 15): 5.2260462733302715, dt.date(2007, 5, 15): 5.152455041052763, dt.date(2007, 6, 15): 5.153305022495742, dt.date(2007, 7, 15): 5.194380721061229, dt.date(2007, 8, 15): 5.219539857041744, dt.date(2007, 9, 15): 5.2835580183334, dt.date(2007, 10, 15): 5.1546838004992654, dt.date(2007, 11, 15): 5.116608778380079, dt.date(2007, 12, 15): 5.092406169461175, dt.date(2008, 1, 15): 5.075316392087712, dt.date(2008, 2, 15): 5.086772198019893, dt.date(2008, 3, 15): 5.077159315000506, dt.date(2008, 4, 15): 5.164390743356619, dt.date(2008, 5, 15): 5.141766490905071, dt.date(2008, 6, 15): 5.08124524079358, dt.date(2008, 7, 15): 5.180528670996194, dt.date(2008, 8, 15): 5.20411228596646, dt.date(2008, 9, 15): 5.2730543319696634, dt.date(2008, 10, 15): 5.149544345980972, dt.date(2008, 11, 15): 5.1071887628028945, dt.date(2008, 12, 15): 5.099698161447165, dt.date(2009, 1, 15): 5.096671600851375, dt.date(2009, 2, 15): 5.073660419754621, dt.date(2009, 3, 15): 5.10535794282341, dt.date(2009, 4, 15): 5.180995654124148, dt.date(2009, 5, 15): 5.185950719137308, dt.date(2009, 6, 15): 5.1264494980956945, dt.date(2009, 7, 15): 5.198517056758129, dt.date(2009, 8, 15): 5.255481879156899, dt.date(2009, 9, 15): 5.226693874927456, dt.date(2009, 10, 15): 5.164760639327689, dt.date(2009, 11, 15): 5.07779899878068, dt.date(2009, 12, 15): 5.062805153934975, dt.date(2010, 1, 15): 5.055880808519881, dt.date(2010, 2, 15): 5.08000823297788, dt.date(2010, 3, 15): 5.072383253270307, dt.date(2010, 4, 15): 5.134670464622906, dt.date(2010, 5, 15): 5.114834017687322, dt.date(2010, 6, 15): 5.086562995713622, dt.date(2010, 7, 15): 5.174505559827488, dt.date(2010, 8, 15): 5.205859935137845, dt.date(2010, 9, 15): 5.197875848368508, dt.date(2010, 10, 15): 5.157963972297686, dt.date(2010, 11, 15): 5.119720132380603, dt.date(2010, 12, 15): 5.068699302261731, dt.date(2011, 1, 15): 5.076600305473439, dt.date(2011, 2, 15): 5.053054749448979, dt.date(2011, 3, 15): 5.065655287636269, dt.date(2011, 4, 15): 5.171829568142723, dt.date(2011, 5, 15): 5.089895554402875, dt.date(2011, 6, 15): 5.06983108239176, dt.date(2011, 7, 15): 5.214108535199882, dt.date(2011, 8, 15): 5.222466919623494, dt.date(2011, 9, 15): 5.216275065657039, dt.date(2011, 10, 15): 5.169114386002532, dt.date(2011, 11, 15): 5.090980337043401, dt.date(2011, 12, 15): 5.074818343892969, dt.date(2012, 1, 15): 5.075121842468078, dt.date(2012, 2, 15): 5.052278557846082, dt.date(2012, 3, 15): 5.089590778415986, dt.date(2012, 4, 15): 5.166811548705983, dt.date(2012, 5, 15): 5.11815236152917, dt.date(2012, 6, 15): 5.078850311990573, dt.date(2012, 7, 15): 5.160116316841403, dt.date(2012, 8, 15): 5.17058259648964, dt.date(2012, 9, 15): 5.220133695328236, dt.date(2012, 10, 15): 5.1093780211571485, dt.date(2012, 11, 15): 5.064980591208316, dt.date(2012, 12, 15): 5.057011930246192, dt.date(2013, 1, 15): 5.062314516116726, dt.date(2013, 2, 15): 5.031589266980347, dt.date(2013, 3, 15): 5.08297420392068, dt.date(2013, 4, 15): 5.163531902491466, dt.date(2013, 5, 15): 5.117751913342345, dt.date(2013, 6, 15): 5.075662025934803, dt.date(2013, 7, 15): 5.156341600047443, dt.date(2013, 8, 15): 5.168989621443111, dt.date(2013, 9, 15): 5.182785770892909, dt.date(2013, 10, 15): 5.156518484877244, dt.date(2013, 11, 15): 5.060204710110696, dt.date(2013, 12, 15): 5.045827830803974, dt.date(2014, 1, 15): 5.035521726668373, dt.date(2014, 2, 15): 5.015037414111919, dt.date(2014, 3, 15): 5.055617541189106, dt.date(2014, 4, 15): 5.145007910967305, dt.date(2014, 5, 15): 5.103829855749034, dt.date(2014, 6, 15): 5.08364762915354, dt.date(2014, 7, 15): 5.159447845307392, dt.date(2014, 8, 15): 5.194210580897562, dt.date(2014, 9, 15): 5.200321618622149, dt.date(2014, 10, 15): 5.086049478025545, dt.date(2014, 11, 15): 5.061117458948199, dt.date(2014, 12, 15): 5.043965806908714, dt.date(2015, 1, 15): 5.050892280160563, dt.date(2015, 2, 15): 5.043173257447929, dt.date(2015, 3, 15): 5.0714114839067435, dt.date(2015, 4, 15): 5.150454897387446, dt.date(2015, 5, 15): 5.118327382059873, dt.date(2015, 6, 15): 5.112722543269251, dt.date(2015, 7, 15): 5.184968077160455, dt.date(2015, 8, 15): 5.1954331363923005, dt.date(2015, 9, 15): 5.232054654548663, dt.date(2015, 10, 15): 5.097266441737884, dt.date(2015, 11, 15): 5.088762334799119, dt.date(2015, 12, 15): 5.058043738934319}
    return shannon_index


# Applies FFT to the shannon values and decomposes the plot into low and high frequency
def shannon_fourier_decomposed(shannon_values, name=None):
    values = list(shannon_values.values())
    n = len(values)  # Number of samples

    # Perform Fourier Transform
    fft_values = np.fft.fft(values)
    frequencies = np.fft.fftfreq(n)

    # Separate components
    dc_component = np.zeros_like(fft_values)
    dc_component[0] = fft_values[0]

    low_frequency_component = np.zeros_like(fft_values)
    high_frequency_component = np.zeros_like(fft_values)

    cutoff_frequency = 0.1
    low_frequency_component[np.abs(frequencies) < cutoff_frequency] = fft_values[np.abs(frequencies) < cutoff_frequency]

    high_frequency_component[np.abs(frequencies) >= cutoff_frequency] = fft_values[np.abs(frequencies) >= cutoff_frequency]

    # Reconstruct each component
    dc_reconstructed = np.fft.ifft(dc_component).real
    low_frequency_reconstructed = np.fft.ifft(low_frequency_component).real
    high_frequency_reconstructed = np.fft.ifft(high_frequency_component).real

    # Plot original and components
    if name != None:
        plt.figure(figsize=(12, 10))

        plt.subplot(3, 1, 1)
        plt.plot(values, label="Original Data", color='black')
        plt.title("Original Data")
        plt.legend()

        plt.subplot(3, 1, 2)
        plt.plot(low_frequency_reconstructed, label="Low-Frequency Component (Trend)", color='blue')
        plt.title("Low-Frequency Component (Trend)")
        plt.legend()

        plt.subplot(3, 1, 3)
        plt.plot(high_frequency_reconstructed, label="High-Frequency Component (Fluctuations)", color='red')
        plt.title("High-Frequency Component (Fluctuations)")
        plt.legend()

        plt.tight_layout()
        plt.savefig(f'{name}.png')

        result_high = adfuller(high_frequency_reconstructed)
        print("High-Frequency Component ADF Test:")
        print(f"ADF Statistic: {result_high[0]}")
        print(f"P-Value: {result_high[1]}")
        result_low = adfuller(low_frequency_reconstructed)
        print("\nLow-Frequency Component ADF Test:")
        print(f"ADF Statistic: {result_low[0]}")
        print(f"P-Value: {result_low[1]}")

        result_high_kpss = kpss(high_frequency_reconstructed)
        print("High-Frequency Component KPSS Test:")
        print(f"KPSS Statistic: {result_high_kpss[0]}")
        print(f"P-Value: {result_high_kpss[1]}")
        result_low_kpss = kpss(low_frequency_reconstructed)
        print("\nLow-Frequency Component KPSS Test:")
        print(f"KPSS Statistic: {result_low_kpss[0]}")
        print(f"P-Value: {result_low_kpss[1]}")


    keys = list(shannon_values.keys())
    decomposed_values = {key: value for key, value in zip(keys, high_frequency_reconstructed)}
    return decomposed_values


# Calculates shannon index
def calc_shannon(species_counts):
    total_sightings = sum(species_counts.values())
    shannon_index = 0
    for count in species_counts.values():
        p_i = count / total_sightings
        shannon_index -= p_i * math.log(p_i)
    return shannon_index


# Calc shannon index by day, requires file to be sorted by date
def shannon_index_by_day(file_path):
    with open(file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter='\t')
        csv_reader.fieldnames = [name.strip() for name in csv_reader.fieldnames]

        species_counts = Counter()
        shannon_values = {}
        current_date = None

        print("beginning shannon calc per day...")
        for row in csv_reader:
            date = row["OBSERVATION DATE"].strip()
            y, m, d = date.split('-')
            next_date = dt.date(int(y), int(m), int(d))

            if current_date is None:
                # First date in the file
                current_date = next_date

            if next_date > current_date:
                # Calculate Shannon index for the previous day
                shannon_index = calc_shannon(species_counts)
                shannon_values[current_date] = shannon_index

                # Transition to the next day
                current_date = next_date
                species_counts.clear()

            # Add species for the current row
            common_name = row["COMMON NAME"].strip()
            species_counts[common_name] += 1

        # Handle final day's data
        if species_counts:
            shannon_index = calc_shannon(species_counts)
            shannon_values[current_date] = shannon_index

    # print(shannon_values)
    return shannon_values


# Shannon index of whole dataset
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


# Shannon index for given yy-mm
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
            elif int(y) == year and int(m) > month:
                break

    total_sightings = sum(species_counts.values())
    shannon_index = 0
    for count in species_counts.values():
        p_i = count / total_sightings
        shannon_index -= p_i * math.log(p_i)
    return shannon_index


# Helper function that made database more manageable
def shannon_concatenate_days():
    years = [2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015]
    all_shannon_values = {}
    for year in years:
        shannon_values = shannon_index_by_day(f'sorted{year}.txt')
        all_shannon_values.update(shannon_values)
    return all_shannon_values


# Plots shannon values
def plot_shannon(shannon_values):
    dates_shannon = list(shannon_values.keys())
    values_shannon = list(shannon_values.values())
    plt.figure(figsize=(10, 6))
    plt.plot(dates_shannon, values_shannon, label='shannon index')

    plt.title('Shannon-index by month in CA (2006-2015)', fontsize=14)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Value', fontsize=12)

    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=10)

    plt.tight_layout()
    plt.show()

