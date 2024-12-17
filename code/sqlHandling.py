import sqlite3
import matplotlib.pyplot as plt
import datetime as dt
from collections import defaultdict
from scipy.ndimage import gaussian_filter1d
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.preprocessing import StandardScaler
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

# fit fires dataset which is based on days, to the total acres burnt in that month
def fit_fires_to_months(fires):
    monthly_fires = defaultdict(int)
    for date, amount in fires.items():
        # month = date.strftime('%Y-%m')  # Format as 'YYYY-MM'
        index = dt.date(date.year, date.month, 15)
        monthly_fires[index] += amount
    monthly_fires = dict(monthly_fires)
    return monthly_fires


# convert Julian_day to gregorian
def get_real_date(julian_day):
    julian_base = 1721424.5  # Julian Day 0 blijkbaar
    gregorian_ordinal = int(julian_day - julian_base)
    return dt.date.fromordinal(gregorian_ordinal)


def linear_regression_fires_counties(fires, shannon_values, county_name="All", days=False):
    print(county_name)
    aggregated_fires = defaultdict(int)
    if county_name == "All":
        for county_data in fires.values():
            for date, fire_size in county_data.items():
                aggregated_fires[date] += fire_size
    else:
        county_data = fires.get(county_name.lower(), {})
        for date, fire_size in county_data.items():
            aggregated_fires[date] += fire_size

    if days:
        for date in shannon_values:
            if aggregated_fires.get(date, False) == False:
                aggregated_fires[date] = 0

    dates_fires = list(aggregated_fires.keys())
    dates_shannon = list(shannon_values.keys())
    X = np.array([aggregated_fires[date] for date in dates_shannon]).reshape(-1, 1)
    y = np.array([shannon_values[date] for date in dates_shannon])

    x_normalized = (X - X.min()) / (X.max() - X.min())

    model = LinearRegression()
    model.fit(x_normalized, y)

    slope = model.coef_[0]
    intercept = model.intercept_

    y_pred = model.predict(x_normalized)

    r2 = r2_score(y, y_pred)
    X_with_const = sm.add_constant(x_normalized)
    sm_model = sm.OLS(y, X_with_const).fit()
    p_value = sm_model.pvalues[1]

    print("p-value slope: ", p_value)
    print(f"Slope: {slope}, Intercept: {intercept}, R²: {r2}")
    plt.scatter(x_normalized, y, color='blue', label='Data')
    plt.plot(x_normalized, y_pred, color='red', label='Regression Line')
    plt.title(f'Linear regression {county_name} (2006-2015)', fontsize=14)
    plt.xlabel('Wildfires (Acres Burnt)')
    plt.ylabel('Shannon Index')
    plt.ylim(-3, 3)
    plt.legend()
    plt.savefig(f"regression_{county_name}.png")
    plt.close()


def linear_regression_fires(fires, shannon_values, county_name="All", days=False):
    if days:
        print("check")
        for date in shannon_values:
            if fires.get(date, False) == False:
                fires[date] = 0

    dates_fires = list(fires.keys())
    dates_shannon = list(shannon_values.keys())
    X = np.array(list(fires.values())).reshape(-1, 1)
    y = np.array(list(shannon_values.values()))
    # scaler = StandardScaler()
    # x_normalized = scaler.fit_transform(X.reshape(-1, 1))
    x_normalized = (X - X.min()) / (X.max() - X.min())
    # Create and fit the model
    model = LinearRegression()
    model.fit(x_normalized, y)

    slope = model.coef_[0]
    intercept = model.intercept_

    # Predict Shannon index based on wildfire data
    y_pred = model.predict(x_normalized)

    r2 = r2_score(y, y_pred)

    X_with_const = sm.add_constant(x_normalized)  # Add intercept to the model
    sm_model = sm.OLS(y, X_with_const).fit()
    p_value = sm_model.pvalues[1]  # p-value for the slope coefficient
    print("p-value slope: ", p_value)

    print(f"Slope: {slope}, Intercept: {intercept}, R²: {r2}")
    plt.scatter(x_normalized, shannon_values.values(), color='blue', label='Data')
    plt.plot(x_normalized, y_pred, color='red', label='Regression Line')
    plt.title(f'Linear regression {county_name} (2006-2015)', fontsize=14)
    plt.xlabel('Wildfires (Acres Burnt)')
    plt.xlim(0, 0.001)  # Focus on the dense cluster
    # plt.xscale('log')
    plt.ylabel('Shannon Index')
    plt.legend()
    plt.show()
    plt.close()

def extract_fires(db_path, county, county_code=None):
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

    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    fig.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', fontsize=10,
               bbox_to_anchor=(0.8, 0.9))

    plt.grid(True, linestyle='--', alpha=0.6)
    plt.title('Amount of acres burnt in CA against shannon index (2006-2015)', fontsize=14)
    fig.tight_layout()
    plt.savefig('shannon_values_fires.png')
    plt.show()


# db_path = 'data/firedata.sqlite'
# fires = extract_fires(db_path, 'All')
# max_fires = max(zip(fires.values(), fires.keys()))
# print("Date with the largest fire:", max_fires)
# shannon_values = shannon_calculation.shannon_index_by_month_CA()
# shannon_calculation.shannon_fourier_decomposed(shannon_values)
# monthly_fires = fit_fires_to_months(fires)
# plot_shannon_fires(monthly_fires, shannon_values)
# plot_shannon_fires(fires, decomposed_values)
