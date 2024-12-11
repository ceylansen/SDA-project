import sqlite3
import numpy as np
from scipy.fft import fft, fftfreq
import csv
import math
from collections import Counter
import matplotlib.pyplot as plt
import datetime
import sys

def shannon_index_by_month_CA():
    shannon_index = {datetime.date(2006, 1, 15): 5.13392382109124, datetime.date(2006, 2, 15): 5.113348158753306, datetime.date(2006, 3, 15): 5.114262021259862, datetime.date(2006, 4, 15): 5.224760883557517, datetime.date(2006, 5, 15): 5.171996817626759, datetime.date(2006, 6, 15): 5.136022591043768, datetime.date(2006, 7, 15): 5.237388261032557, datetime.date(2006, 8, 15): 5.283679535122384, datetime.date(2006, 9, 15): 5.312001380553248, datetime.date(2006, 10, 15): 5.2334501636047115, datetime.date(2006, 11, 15): 5.1513741347162565, datetime.date(2006, 12, 15): 5.143742602095986, datetime.date(2007, 1, 15): 5.129459973668558, datetime.date(2007, 2, 15): 5.093402547566193, datetime.date(2007, 3, 15): 5.107668262537926, datetime.date(2007, 4, 15): 5.2260462733302715, datetime.date(2007, 5, 15): 5.152455041052763, datetime.date(2007, 6, 15): 5.153305022495742, datetime.date(2007, 7, 15): 5.194380721061229, datetime.date(2007, 8, 15): 5.219539857041744, datetime.date(2007, 9, 15): 5.2835580183334, datetime.date(2007, 10, 15): 5.1546838004992654, datetime.date(2007, 11, 15): 5.116608778380079, datetime.date(2007, 12, 15): 5.092406169461175, datetime.date(2008, 1, 15): 5.075316392087712, datetime.date(2008, 2, 15): 5.086772198019893, datetime.date(2008, 3, 15): 5.077159315000506, datetime.date(2008, 4, 15): 5.164390743356619, datetime.date(2008, 5, 15): 5.141766490905071, datetime.date(2008, 6, 15): 5.08124524079358, datetime.date(2008, 7, 15): 5.180528670996194, datetime.date(2008, 8, 15): 5.20411228596646, datetime.date(2008, 9, 15): 5.2730543319696634, datetime.date(2008, 10, 15): 5.149544345980972, datetime.date(2008, 11, 15): 5.1071887628028945, datetime.date(2008, 12, 15): 5.099698161447165, datetime.date(2009, 1, 15): 5.096671600851375, datetime.date(2009, 2, 15): 5.073660419754621, datetime.date(2009, 3, 15): 5.10535794282341, datetime.date(2009, 4, 15): 5.180995654124148, datetime.date(2009, 5, 15): 5.185950719137308, datetime.date(2009, 6, 15): 5.1264494980956945, datetime.date(2009, 7, 15): 5.198517056758129, datetime.date(2009, 8, 15): 5.255481879156899, datetime.date(2009, 9, 15): 5.226693874927456, datetime.date(2009, 10, 15): 5.164760639327689, datetime.date(2009, 11, 15): 5.07779899878068, datetime.date(2009, 12, 15): 5.062805153934975, datetime.date(2010, 1, 15): 5.055880808519881, datetime.date(2010, 2, 15): 5.08000823297788, datetime.date(2010, 3, 15): 5.072383253270307, datetime.date(2010, 4, 15): 5.134670464622906, datetime.date(2010, 5, 15): 5.114834017687322, datetime.date(2010, 6, 15): 5.086562995713622, datetime.date(2010, 7, 15): 5.174505559827488, datetime.date(2010, 8, 15): 5.205859935137845, datetime.date(2010, 9, 15): 5.197875848368508, datetime.date(2010, 10, 15): 5.157963972297686, datetime.date(2010, 11, 15): 5.119720132380603, datetime.date(2010, 12, 15): 5.068699302261731, datetime.date(2011, 1, 15): 5.076600305473439, datetime.date(2011, 2, 15): 5.053054749448979, datetime.date(2011, 3, 15): 5.065655287636269, datetime.date(2011, 4, 15): 5.171829568142723, datetime.date(2011, 5, 15): 5.089895554402875, datetime.date(2011, 6, 15): 5.06983108239176, datetime.date(2011, 7, 15): 5.214108535199882, datetime.date(2011, 8, 15): 5.222466919623494, datetime.date(2011, 9, 15): 5.216275065657039, datetime.date(2011, 10, 15): 5.169114386002532, datetime.date(2011, 11, 15): 5.090980337043401, datetime.date(2011, 12, 15): 5.074818343892969, datetime.date(2012, 1, 15): 5.075121842468078, datetime.date(2012, 2, 15): 5.052278557846082, datetime.date(2012, 3, 15): 5.089590778415986, datetime.date(2012, 4, 15): 5.166811548705983, datetime.date(2012, 5, 15): 5.11815236152917, datetime.date(2012, 6, 15): 5.078850311990573, datetime.date(2012, 7, 15): 5.160116316841403, datetime.date(2012, 8, 15): 5.17058259648964, datetime.date(2012, 9, 15): 5.220133695328236, datetime.date(2012, 10, 15): 5.1093780211571485, datetime.date(2012, 11, 15): 5.064980591208316, datetime.date(2012, 12, 15): 5.057011930246192, datetime.date(2013, 1, 15): 5.062314516116726, datetime.date(2013, 2, 15): 5.031589266980347, datetime.date(2013, 3, 15): 5.08297420392068, datetime.date(2013, 4, 15): 5.163531902491466, datetime.date(2013, 5, 15): 5.117751913342345, datetime.date(2013, 6, 15): 5.075662025934803, datetime.date(2013, 7, 15): 5.156341600047443, datetime.date(2013, 8, 15): 5.168989621443111, datetime.date(2013, 9, 15): 5.182785770892909, datetime.date(2013, 10, 15): 5.156518484877244, datetime.date(2013, 11, 15): 5.060204710110696, datetime.date(2013, 12, 15): 5.045827830803974, datetime.date(2014, 1, 15): 5.035521726668373, datetime.date(2014, 2, 15): 5.015037414111919, datetime.date(2014, 3, 15): 5.055617541189106, datetime.date(2014, 4, 15): 5.145007910967305, datetime.date(2014, 5, 15): 5.103829855749034, datetime.date(2014, 6, 15): 5.08364762915354, datetime.date(2014, 7, 15): 5.159447845307392, datetime.date(2014, 8, 15): 5.194210580897562, datetime.date(2014, 9, 15): 5.200321618622149, datetime.date(2014, 10, 15): 5.086049478025545, datetime.date(2014, 11, 15): 5.061117458948199, datetime.date(2014, 12, 15): 5.043965806908714, datetime.date(2015, 1, 15): 5.050892280160563, datetime.date(2015, 2, 15): 5.043173257447929, datetime.date(2015, 3, 15): 5.0714114839067435, datetime.date(2015, 4, 15): 5.150454897387446, datetime.date(2015, 5, 15): 5.118327382059873, datetime.date(2015, 6, 15): 5.112722543269251, datetime.date(2015, 7, 15): 5.184968077160455, datetime.date(2015, 8, 15): 5.1954331363923005, datetime.date(2015, 9, 15): 5.232054654548663, datetime.date(2015, 10, 15): 5.097266441737884, datetime.date(2015, 11, 15): 5.088762334799119, datetime.date(2015, 12, 15): 5.058043738934319}
    return shannon_index


def shannon_diff(shannon_values):
    pass


def shannon_fourier(shannon_values):
    # sorted_data = dict(sorted(shannon_values.items(), key=lambda x: datetime.strptime(x[0], '%Y-%m-%d')))
    # values = list(sorted_data.values())
    values = list(shannon_values.values())
    # values = values - np.mean(values)
    # n = len(values)
    # fft_values = fft(values)
    # frequencies = fftfreq(len(values), 1)
    # positive_frequencies = frequencies[:n // 2]
    # positive_magnitudes = np.abs(fft_values[:n // 2])
    # print(fft_values)
    # print(frequencies)
    n = len(values)  # Number of samples

    # Perform Fourier Transform
    fft_values = np.fft.fft(values)
    frequencies = np.fft.fftfreq(n)

    # Remove DC Component (mean)
    fft_values[0] = 0

    # Optional: Remove Low-Frequency Components (apply high-pass filter)
    cutoff_frequency = 0.1  # Adjust this based on your data
    fft_values[np.abs(frequencies) < cutoff_frequency] = 0

    # Perform Inverse Fourier Transform to get stationary data
    stationary_line = np.fft.ifft(fft_values).real
    plt.figure(figsize=(10,8))
    # plt.plot(positive_frequencies, positive_magnitudes, marker='o', label="Frequency Spectrum")
    # plt.title("Frequency Spectrum")
    # plt.xlabel("Frequency")
    # plt.ylabel("Magnitude")
    # plt.legend()
    # plt.title('FFT Analysis')
    # plt.show()
    plt.title("Stationary Line (Trend Removed)")
    plt.plot(stationary_line, marker='o', label="Stationary Line")
    plt.xlabel("Index")
    plt.ylabel("Amplitude")
    plt.show()
    return fft_values



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
    plt.savefig('Shannon_index_seperate.png')


file_path = 'data/ebd_2006_2015.txt'
column_name = 'COMMON NAME'
state = 'CA'
county = 'All'
db_path = 'data/firedata.sqlite'
if len(sys.argv) > 1:
    county = sys.argv[1]

values = shannon_index_by_month_CA()
shannon_fourier(values)
# plot_shannon(values)