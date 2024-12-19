import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from collections import defaultdict
from scipy.signal import correlate
import shannon_fires, shannon_calculation, sqlHandling
import seaborn as sns
from scipy.signal import detrend


# Fit shannon values to monthly intervals
def fit_shannon_to_months_avg(shannon_values, test=False):
    monthly_totals = {}
    monthly_counts = {}

    # Aggregate values into months
    for date, value in shannon_values.items():
        month = dt.date(date.year, date.month, 15)
        if month in monthly_totals:
            monthly_totals[month] += value
            monthly_counts[month] += 1
        else:
            monthly_totals[month] = value
            monthly_counts[month] = 1

    # Ensure all months are present
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


# Fit fire data to monthly intervals
def fit_fires_to_months(fires, testing=False):
    monthly_fires = defaultdict(int)
    for date, amount in fires.items():
        # month = date.strftime('%Y-%m')  # Format as 'YYYY-MM'
        index = dt.date(date.year, date.month, 15)
        monthly_fires[index] += amount
    monthly_fires = dict(monthly_fires)

    if testing:
        for year in range(2006, 2009):
            for month in range(1, 13):
                if year == 2008 and month > 10:
                    break
                date = dt.date(year, month, 15)
                if date not in monthly_fires:
                    monthly_fires[date] = 0
    else:
        for year in range(2006, 2016):
            for month in range(1, 13):
                date = dt.date(year, month, 15)
                if date not in monthly_fires:
                    monthly_fires[date] = 0

    return monthly_fires


# Equalizes two dicts, so that all keys are shared
def equalize_dicts(dict1, dict2):
    new_dict1 = {}
    new_dict2 = {}
    for key in dict1.keys():
        if dict1.get(key, False) and dict2.get(key, False):
            new_dict1[key] = dict1[key]
            new_dict2[key] = dict2[key]
    return new_dict1, new_dict2


# Applies cross-correlation to find best lag and best correlation between given fires
# and shannon values
def cross_correlate(shannon_values, fires, name=None):
    shannon_array = np.array(list(shannon_values.values()))
    fires_array = np.array(list(fires.values()))

    shannon_array = (shannon_array - np.mean(shannon_array)) / np.std(shannon_array)
    fires_array = (fires_array - np.mean(fires_array)) / np.std(fires_array)

    lag = np.arange(-len(shannon_array) + 1, len(fires_array))
    cross_corr = correlate(shannon_array, fires_array, mode='full', method='fft')

    max_lag_index = np.argmax(np.abs(cross_corr))
    best_lag = lag[max_lag_index]
    best_correlation = cross_corr[max_lag_index]
    print("best lag: ", best_lag)
    print("corresponding correlation value: ", best_correlation)

    if name != None:
        plt.plot(lag, cross_corr)
        plt.xlabel('Lag (months)')
        plt.ylabel('Cross-Correlation')
        plt.title('Cross-Correlation Between Acres Burnt and Shannon Index')
        plt.savefig(f'{name}.png')
    return best_lag, best_correlation


# Plots cross-correlate results
def plot_lag_results(best_lags, best_correlations, name):
    fig, axs = plt.subplots(1, 3, figsize=(18, 6))

    # Histogram of best lags
    sns.histplot(best_lags, bins=20, kde=True, ax=axs[0], color='blue')
    axs[0].set_title('Best Lags', fontsize=14)
    axs[0].set_xlabel('Lag', fontsize=12)
    axs[0].set_ylabel('Frequency', fontsize=12)

    # Histogram of best correlations
    sns.histplot(best_correlations, bins=20, kde=True, ax=axs[1], color='green')
    axs[1].set_title('Correlation Values', fontsize=14)
    axs[1].set_xlabel('Correlation', fontsize=12)
    axs[1].set_ylabel('Frequency', fontsize=12)

    # Scatter plot of lags vs. correlations
    sns.scatterplot(x=best_lags, y=best_correlations, ax=axs[2], color='purple')
    axs[2].set_title('Lags vs. Correlations', fontsize=14)
    axs[2].set_xlabel('Lag', fontsize=12)
    axs[2].set_ylabel('Correlation', fontsize=12)
    axs[2].grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(f"plots/{name}_lag_results.png")
    plt.close(fig)

