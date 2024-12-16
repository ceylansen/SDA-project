import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
from scipy.signal import correlate
import shannon_fires, shannon_calculation, sqlHandling

def fit_shannon_to_months(shannon_values):
    monthly_totals = {}  # To store the sum of values for each month
    monthly_counts = {}  # To store the count of values for each month

    for date, value in shannon_values.items():
        month = (date.year, date.month)
        if month in monthly_totals.keys():
            monthly_totals[month] += value
            monthly_counts[month] += 1
        else:
            monthly_totals[month] = 1
            monthly_counts[month] = 1

    # Calculate the average for each month
    monthly_averages = {
        month: monthly_totals[month] / monthly_counts[month]
        for month in monthly_totals
    }
    return monthly_averages


def cross_correlate(max_lag, shannon_values, fires):
    sorted_county = shannon_fires.sort_county_by_date(bird_path, 'ebird_counties_datesorted.txt', 'Humboldt')
    shannon_day_values = shannon_fires.shannon_index_by_day_for_array(sorted_county)
    decomposed_values = shannon_calculation.shannon_fourier_decomposed(shannon_day_values)
    # shannon_calculation.plot_shannon(decomposed_values)
    # Assuming 'acres_burnt' and 'shannon_fluctuations' are your time series
    lag = np.arange(-max_lag, max_lag + 1)
    cross_corr = correlate(shannon_values, fires.values(), mode='full', method='fft')
    lags = lag[np.argmax(cross_corr)]  # Find lag with highest correlation

    plt.plot(lag, cross_corr)
    plt.xlabel('Lag (days)')
    plt.ylabel('Cross-Correlation')
    plt.title('Cross-Correlation Between Acres Burnt and Shannon Index')
    plt.show()

db_path = "data/firedata.sqlite"
bird_path = "data/filtered_for_counties.txt"
fires = shannon_fires.extract_all_fires(db_path)
sorted_county = shannon_fires.sort_county_by_date(bird_path, 'ebird_counties_datesorted.txt', 'Humboldt')
shannon_day_values = shannon_fires.shannon_index_by_day_for_array(sorted_county)
decomposed_values = shannon_calculation.shannon_fourier_decomposed(shannon_day_values)
print("shannon")
print(len(decomposed_values))
print(len(fit_shannon_to_months(decomposed_values)))
print("fires")
print(len(fires['humboldt']))
print(sqlHandling.fit_fires_to_months(fires['humboldt']))
