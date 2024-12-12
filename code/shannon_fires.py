import sqlite3
import matplotlib.pyplot as plt
import datetime as dt
import random

import shannon_calculation
import sqlHandling

DAYSPOSTFIRE = 365



def get_largest_fires(fires, county):
    largest_fires = sorted(fires.items(), key=lambda x: x[1], reverse=True)[:5]
    dates, sizes = zip(*largest_fires)
    return dates, sizes

def plot_shannon_test(dates, shannon_values):
    shannon_dates = list(shannon_values.keys())

    fig, axs = plt.subplots(3, 2, figsize=(12, 10))
    axs = axs.flatten()

    for i, fire_date in enumerate(dates):
        fire_date_dt = fire_date
        end_date = fire_date_dt + dt.timedelta(days=DAYSPOSTFIRE)

        filtered_dates = [d for d in shannon_dates if fire_date_dt <= d <= end_date]
        filtered_values = [shannon_values[d] for d in filtered_dates]

        axs[i].plot(filtered_dates, filtered_values)
        axs[i].set_title(f"Shannon Index after Fire {i+1} ({fire_date})")
        axs[i].set_xlabel("Date")
        axs[i].set_ylabel("Shannon Index")

    random_date = random.choice([d for d in shannon_dates if d <= max(shannon_dates) - dt.timedelta(days=DAYSPOSTFIRE)])
    end_date = random_date + dt.timedelta(days=DAYSPOSTFIRE)

    filtered_dates = [d for d in shannon_dates if random_date <= d <= end_date]
    filtered_values = [shannon_values[d] for d in filtered_dates]

    axs[5].plot(filtered_dates, filtered_values)
    axs[5].set_title(f"Shannon Index after Random Date ({random_date})")
    axs[5].set_xlabel("Date")
    axs[5].set_ylabel("Shannon Index")

    plt.tight_layout()
    plt.savefig("shannon_tests_lassen")

db_path = "data/firedata.sqlite"
bird_path = "data/lassen0615.txt"
county = "Lassen"
county_code = 35
fires = sqlHandling.extract_fires(db_path, county, county_code)
dates, sizes = get_largest_fires(fires, county)
# shannon_values = shannon_calculation.shannon_index_by_month_CA()
shannon_values = {}
years = list(range(2006, 2016))
months = list(range(1, 13))
for year in years:
    for month in months:
        shannon_values[dt.date(year, month, 15)] = shannon_calculation.shannon_index_by_month(bird_path, month, year)
decomposed_values = shannon_calculation.shannon_fourier_decomposed(shannon_values)
plot_shannon_test(dates, decomposed_values)
