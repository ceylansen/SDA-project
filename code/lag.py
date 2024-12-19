import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from collections import defaultdict
from scipy.signal import correlate
import shannon_fires, shannon_calculation, sqlHandling
# from population import count_total_bird_population_by_county, adjust_for_userbase
from scipy.signal import detrend

def fit_shannon_to_months_avg(shannon_values, test=False):
    monthly_totals = {}  # To store the sum of values for each month
    monthly_counts = {}  # To store the count of values for each month

    # Aggregate values into months
    for date, value in shannon_values.items():
        month = dt.date(date.year, date.month, 15)  # Use the 15th as the representative date
        if month in monthly_totals:
            monthly_totals[month] += value
            monthly_counts[month] += 1
        else:
            monthly_totals[month] = value
            monthly_counts[month] = 1
    # print(monthly_totals.keys())

    # Ensure all months from 2006 to 2016 are represented
    if test:
        for year in range(2006, 2008):
            for month in range(1, 13):
                if year == 2008 and month > 10:
                    break
                date = dt.date(year, month, 15)
                if date not in monthly_totals:
                    monthly_totals[date] = 0
                    monthly_counts[date] = 0
    else:
        for year in range(2006, 2016):
            for month in range(1, 13):
                date = dt.date(year, month, 15)
                if date not in monthly_totals:
                    monthly_totals[date] = 0
                    monthly_counts[date] = 0

    # Calculate the average for each month
    monthly_averages = {
        month: (monthly_totals[month] / monthly_counts[month]) if monthly_counts[month] > 0 else 0
        for month in monthly_totals
    }
    sorted_monthly_averages = dict(sorted(monthly_averages.items()))
    return sorted_monthly_averages


def fit_fires_to_months(fires):
    monthly_fires = defaultdict(int)
    for date, amount in fires.items():
        # month = date.strftime('%Y-%m')  # Format as 'YYYY-MM'
        index = dt.date(date.year, date.month, 15)
        monthly_fires[index] += amount
    monthly_fires = dict(monthly_fires)

    for year in range(2006, 2016):
        for month in range(1, 13):
            date = dt.date(year, month, 15)
            if date not in monthly_fires:
                monthly_fires[date] = 0

    return monthly_fires


def cross_correlate(shannon_values, fires):
    shannon_array = np.array(list(shannon_values.values()))
    fires_array = np.array(list(fires.values()))

    # shannon_array = detrend(shannon_array)
    # fires_array = detrend(fires_array)

    shannon_array = (shannon_array - np.mean(shannon_array)) / np.std(shannon_array)
    fires_array = (fires_array - np.mean(fires_array)) / np.std(fires_array)

    # lag = np.arange(-max_lag, max_lag + 1)
    lag = np.arange(-len(shannon_array) + 1, len(fires_array))
    cross_corr = correlate(shannon_array, fires_array, mode='full', method='fft')

    max_lag_index = np.argmax(np.abs(cross_corr))  # Index of max absolute value
    best_lag = lag[max_lag_index]  # Corresponding lag
    best_correlation = cross_corr[max_lag_index]
    print("best lag: ", best_lag)
    print("corresponding correlation value: ", best_correlation)

    # print(lags)
    plt.plot(lag, cross_corr)
    plt.xlabel('Lag (months)')
    plt.ylabel('Cross-Correlation')
    plt.title('Cross-Correlation Between Acres Burnt and Shannon Index')
    plt.show()

def test_cross_correlate():
    db_path = "data/firedata.sqlite"
    bird_path = "data/filtered_for_counties.txt"
    fires = shannon_fires.extract_all_fires(db_path)
    total_observations = count_total_bird_population_by_county('Orange')
    weights = adjust_for_userbase('Orange')
    weighted_observations = { date: count * weights.get(date.year, 1) for date, count in total_observations.items()}
    smoothed_data = gaussian_filter1d(list(weighted_observations.values()), sigma=2)
    smoothed_data_with_keys = dict(zip(weighted_observations.keys(), smoothed_data))
    month_avgs = fit_shannon_to_months_avg(smoothed_data_with_keys)
    decomposed_values = shannon_calculation.shannon_fourier_decomposed(month_avgs)
    monthly_fires = fit_fires_to_months(fires['humboldt'])
    cross_correlate(decomposed_values, monthly_fires)


# test_cross_correlate()
