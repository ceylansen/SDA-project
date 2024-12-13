import sqlite3
import matplotlib.pyplot as plt
import datetime as dt
from collections import defaultdict
from scipy.ndimage import gaussian_filter1d
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import statsmodels.api as sm
import numpy as np

import ebirddatareader
import shannon_calculation

# code voor de bounding box van de hele land bird monitoring data set 2007-2017
# cursor.execute(
#     """
#     SELECT FIRE_YEAR, DISCOVERY_DATE, FIRE_SIZE
#     FROM Fires
#     WHERE LATITUDE BETWEEN 38.6703 AND 39.6335
#     AND LONGITUDE BETWEEN -78.7646 AND -76.7983
#     AND FIRE_YEAR BETWEEN 2007 AND 2015;
#     """
#     )

def fit_fires_to_months(fires):
    monthly_fires = defaultdict(int)
    for date, amount in fires.items():
        # month = date.strftime('%Y-%m')  # Format as 'YYYY-MM'
        index = dt.date(date.year, date.month, 15)
        monthly_fires[index] += amount
    monthly_fires = dict(monthly_fires)
    return monthly_fires


def get_real_date(julian_day):
    julian_base = 1721424.5  # Julian Day 0 blijkbaar
    gregorian_ordinal = int(julian_day - julian_base)
    return dt.date.fromordinal(gregorian_ordinal)


def linear_regression_fires(fires, shannon_values, days=False):
    if days:
        print("check")
        for date in shannon_values:
            if fires.get(date, False) == False:
                fires[date] = 0

    dates_fires = list(fires.keys())
    dates_shannon = list(shannon_values.keys())
    X = np.array(list(fires.values())).reshape(-1, 1)
    y = np.array(list(shannon_values.values()))
    # Create and fit the model
    model = LinearRegression()
    model.fit(X, y)

    # Get coefficients
    slope = model.coef_[0]
    intercept = model.intercept_

    # Predict Shannon index based on wildfire data
    y_pred = model.predict(X)

    # Evaluate the model
    r2 = r2_score(y, y_pred)

    X_with_const = sm.add_constant(X)  # Add intercept to the model
    sm_model = sm.OLS(y, X_with_const).fit()
    p_value = sm_model.pvalues[1]  # p-value for the slope coefficient
    print("p-value slope: ", p_value)

    print(f"Slope: {slope}, Intercept: {intercept}, R²: {r2}")
    plt.scatter(fires.values(), shannon_values.values(), color='blue', label='Data')
    plt.plot(fires.values(), y_pred, color='red', label='Regression Line')
    plt.xlabel('Wildfires (Acres Burnt)')
    # plt.xscale('log')
    plt.ylabel('Shannon Index')
    plt.legend()
    plt.show()


def extract_fires(db_path, county, county_code):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if county == "All":
        cursor.execute(
            """
            SELECT DISCOVERY_DATE, FIRE_SIZE
            FROM Fires
            WHERE STATE = 'CA'
            AND FIRE_YEAR BETWEEN 2006 AND 2015;
            """
        )
    else:
        cursor.execute(
            f"""
            SELECT DISCOVERY_DATE, FIRE_SIZE
            FROM Fires
            WHERE STATE = 'CA'
            AND (COUNTY = {county_code} OR COUNTY LIKE '%{county}%')
            AND FIRE_YEAR BETWEEN 2006 AND 2015;
            """
        )
    rows = cursor.fetchall()
    conn.close()

    fires = {}
    for row in rows:
        julian_date = row[0]
        try:
            gregorian_date = get_real_date(julian_date)
            fire_size = row[1]

            if gregorian_date not in fires:
                fires[gregorian_date] = fire_size
            else:
                fires[gregorian_date] += fire_size
        except ValueError as e:
            print(f"Error converting Julian date {julian_date}: {e}")

    sorted_fires = dict(sorted(fires.items()))
    return sorted_fires


def plot_fires(fires):
    dates = list(fires.keys())
    fire_counts = list(fires.values())

    plt.figure(figsize=(10, 6))
    plt.plot(dates, fire_counts, label='Acres Burnt')

    plt.title('Number of Fires in California (2006-2015)', fontsize=14)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Acres Burnt', fontsize=12)

    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=10)

    plt.tight_layout()
    plt.savefig('fires.png')


def plot_fires_sightings(fires, sightings):
    dates_fires = list(fires.keys())
    fire_counts = list(fires.values())
    dates_sightings = list(sightings.keys())
    sightings_count = list(sightings.values())

    plt.figure(figsize=(10, 6))
    plt.plot(dates_fires, fire_counts, label='Acres Burnt')

    plt.title('Amount of acres burnt in CA (2006-2015)', fontsize=14)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Acres Burnt', fontsize=12)

    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=10)

    plt.tight_layout()
    plt.savefig('fires.png')

    plt.figure(figsize=(10, 6))

    plt.plot(dates_sightings, sightings_count, label='bird counts')

    plt.title('Bird sightings (2006-2015)', fontsize=14)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Count', fontsize=12)

    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=10)

    plt.tight_layout()
    plt.savefig('sightings.png')


def plot_shannon_fires(fires, shannon_values):
    dates_fires = list(fires.keys())
    fire_counts = list(fires.values())
    # smoothed_data = gaussian_filter1d(fire_counts, sigma=5)
    dates_shannon = list(shannon_values.keys())
    values_shannon = list(shannon_values.values())

    # plt.figure(figsize=(10, 6))
    fig, ax1 = plt.subplots()
    ax1.plot(dates_fires, fire_counts, label='Acres Burnt')

    ax1.set_xlabel('Date', fontsize=12)
    ax1.set_ylabel('Acres Burnt', fontsize=12)
    ax1.set_yscale('log')

    ax2 = ax1.twinx()
    ax2.plot(dates_shannon, values_shannon, 'r-', label="Shannon Index")
    ax2.set_ylabel("Shannon Value", color='r')
    ax2.tick_params(axis='y', labelcolor='r')

    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=10)

    plt.title('Amount of acres burnt in CA against shannon index (2006-2015)', fontsize=14)
    fig.tight_layout()
    plt.savefig('shannon_values.png')
    plt.show()


county = "All"
county_code = None
db_path = 'data/firedata.sqlite'
fires = extract_fires(db_path, county, county_code)
max_fires = max(zip(fires.values(), fires.keys()))
file_path_sightings = 'data/ebd_2006_2015.txt'
print("Date with the largest fire:", max_fires)

# plot_fires(fires)
# plot_fires_sightings(fires, ebirddatareader.sightings_per_date(file_path_sightings))
shannon_values = shannon_calculation.shannon_index_by_month_CA()
# shannon_values = shannon_calculation.shannon_concatenate_days()
decomposed_values = shannon_calculation.shannon_fourier_decomposed(shannon_values)

monthly_fires = fit_fires_to_months(fires)
# print(shannon_values)
linear_regression_fires(monthly_fires, decomposed_values, False)
plot_shannon_fires(monthly_fires, decomposed_values)
# plot_shannon_fires(fires, decomposed_values)
