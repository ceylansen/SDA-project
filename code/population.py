import sqlite3
import matplotlib.pyplot as plt
import datetime as dt
import csv
import pandas as pd
from scipy.signal import detrend
from scipy.ndimage import gaussian_filter1d
from collections import Counter
import os
import math
import shannon_fires
import shannon_calculation
from lag import fit_fires_to_months, fit_shannon_to_months_avg, equalize_dicts
import sqlHandling


# Filters dataset for effort, which is classified as unique sampling events
def filter_for_county_effort(input_file, county, output_dir='filtered'):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    with open(input_file, mode='r', encoding='utf-8') as csv_file:
        print("reading in file...")
        csv_reader = csv.DictReader(csv_file, delimiter='\t')
        csv_reader.fieldnames = [name.strip() for name in csv_reader.fieldnames]

        effort_file_path = os.path.join(output_dir, f"filtered_effort_sample.txt")

        print("writing to file")
        with open(effort_file_path, 'w') as effort_file:
            # Write the header to the output file
            effort_file.write(f"OBSERVATION DATE\tSAMPLING EVENT IDENTIFIER\n")
            for row in csv_reader:
                date = row['OBSERVATION DATE'].strip()
                y, m, d = date.split('-')
                if int(y) > 2005 and int(y) < 2009:
                    effort_file.write(f"{row['OBSERVATION DATE']}\t{row['SAMPLING EVENT IDENTIFIER']}\n")


# Counts total bird sightings for a specified county
def count_total_bird_population_by_county(county, file_path):
    print(county)
    sorted_county = shannon_fires.sort_county_by_date(file_path, f'{county}')
    species_counts = Counter()
    shannon_values = {}
    current_date = None
    for row in sorted_county:
        date = row['OBSERVATION DATE'].strip()
        y, m, d = date.split('-')
        next_date = dt.date(int(y), int(m), int(d))

        if current_date is None:
            # First date in the file
            current_date = next_date

        if next_date > current_date:
            # Calculate Shannon index for the previous day
            shannon_values[current_date] = species_counts.total()

            # Transition to the next day
            current_date = next_date
            species_counts.clear()

        # Add species for the current row
        common_name = row["COMMON NAME"].strip()
        species_counts[common_name] += 1

    # Handle the final day's data
    if species_counts:
        shannon_index = shannon_calculation.calc_shannon(species_counts)
        shannon_values[current_date] = shannon_index

    # print(shannon_values)
    # shannon_calculation.plot_shannon(shannon_values)
    return shannon_values


# Plots the bird sightings against the fires for a specific county
def plot_population_fires_county(file_path, fire_path, county, name=None, linreg=False):
    db_path = fire_path
    total_observations = count_total_bird_population_by_county(f'{county}', file_path)
    fires = shannon_fires.extract_all_fires(db_path)

    weights = adjust_for_userbase(county, 'data/filtered_effort_sample.txt')
    weighted_observations = { date: count * weights.get(date.year, 1) for date, count in total_observations.items()}

    smoothed_data = gaussian_filter1d(list(weighted_observations.values()), sigma=2)
    smoothed_data_with_keys = dict(zip(total_observations.keys(), smoothed_data))
    lowercase_county = county.lower()
    county_fires = fires[f'{lowercase_county}']

    avg_populations = fit_shannon_to_months_avg(smoothed_data_with_keys, True)

    detrended_populations = shannon_calculation.shannon_fourier_decomposed(avg_populations)

    monthly_fires = fit_fires_to_months(county_fires, True)

    if linreg == False:
        fig, ax1 = plt.subplots()
        ax1.plot(list(monthly_fires.keys()), list(monthly_fires.values()), label='Acres Burnt')

        ax1.set_xlabel('Date', fontsize=12)
        ax1.set_ylabel('Acres Burnt', fontsize=12)
        ax1.set_yscale('log')

        ax2 = ax1.twinx()
        ax2.plot(list(avg_populations.keys()), list(detrended_populations.values()), 'r-', label="detrended observations")
        ax2.set_ylabel("total observed population", color='r')
        ax2.tick_params(axis='y', labelcolor='r')

        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend(fontsize=10)

        plt.title('Amount of acres burnt in CA against total observations (2006-2015)', fontsize=14)
        fig.tight_layout()
        if name != None:
            plt.savefig(f'plots/{name}.png')
        plt.close()

    # Linear regression part
    if linreg:
        detrended_populations, monthly_fires = equalize_dicts(detrended_populations, monthly_fires)
        r, p_value, r2 = sqlHandling.linear_regression_fires(monthly_fires, detrended_populations, name=f't6_{county}')
        return r, p_value, r2


# Counts unique sampling events
def count_sampling_events(file_path, county=None):
    # return sampling_events
    data = pd.read_csv(file_path, delimiter='\t')

    data['YEAR'] = pd.to_datetime(data['OBSERVATION DATE']).dt.year

    # Filter data for the years 2006 to 2015
    if county != None:
        filtered_data = data[(data['YEAR'] >= 2006) & (data['YEAR'] <= 2015) & data['COUNTY'] == county]
    else:
        filtered_data = data[(data['YEAR'] >= 2006) & (data['YEAR'] <= 2015)]

    # Count unique sampling event identifiers by year
    sampling_events = filtered_data.groupby('YEAR')['SAMPLING EVENT IDENTIFIER'].nunique()

    # print(sampling_events)
    return sampling_events


# Adjusts observation based on weights since ebird had less users in 2006 than 2015
def adjust_for_userbase(county, file_path):
    sampling_events = count_sampling_events(file_path)
    sampling_events_dict = sampling_events.to_dict()
    max_events = max(sampling_events_dict.values())
    weights = {year: max_events / events for year, events in sampling_events.items()}
    return weights

# Plots bird count after being adjusted by effort weights
def plot_adjusted_bird_count(county):
    total_observations = count_total_bird_population_by_county(f'{county}')
    weights = adjust_for_userbase(county)
    weighted_observations = { date: count * weights.get(date.year, 1) for date, count in total_observations.items()}
    smoothed_data = gaussian_filter1d(list(weighted_observations.values()), sigma=2)
    smoothed_data_with_keys = dict(zip(total_observations.keys(), smoothed_data))
    avg_populations = fit_shannon_to_months_avg(smoothed_data_with_keys)
    plt.plot(list(avg_populations.keys()), list(avg_populations.values()), 'r-', label="observations")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=10)
    plt.title(f'average amount of observations each month in {county}')
    plt.show()


def linear_regression_test():
    counties = ['Humboldt', 'Orange', 'Mendocino', 'San Diego', 'San Bernardino']
    for county in counties:
        plot_population_fires_county(f'{county}')
