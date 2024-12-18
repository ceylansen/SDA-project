import sqlite3
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import pandas as pd
from collections import defaultdict
from scipy.ndimage import gaussian_filter1d
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression, HuberRegressor
from sklearn.metrics import r2_score
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm
import numpy as np
import seaborn as sns

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


# Alternate linear regression function
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
    # model = RANSACRegressor(base_estimator=LinearRegression(), random_state=42)
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
    plt.savefig(f"plots/regression_{county_name}.png")
    plt.close()


# Applies linear regression between fires and shannon values and computes pearson coefficient,
# p-value and r2 value
def linear_regression_fires(fires, shannon_values, county_name="All", days=False, name=None):
    if days:
        for date in shannon_values:
            if fires.get(date, False) == False:
                fires[date] = 0

    if len(fires) < 2 or len(shannon_values) < 2:
        return 0, 0, 0

    dates_fires = list(fires.keys())
    dates_shannon = list(shannon_values.keys())
    X = np.array(list(fires.values())).reshape(-1, 1)
    X = np.nan_to_num(X, nan=0.0)
    y = np.array(list(shannon_values.values()))
    x_normalized = (X - X.min()) / (X.max() - X.min())
    x_normalized = np.nan_to_num(x_normalized, nan=0.0)
    model = HuberRegressor()
    model.fit(x_normalized, y)

    slope = model.coef_[0]
    intercept = model.intercept_
    y_pred = model.predict(x_normalized)

    x_new = np.array(list(fires.values()))
    data = {'X': x_new, 'y': y}
    df = pd.DataFrame(data)
    r, p_value = pearsonr(df['X'], df['y'])

    r2 = r2_score(y, y_pred)

    plt.scatter(x_normalized, shannon_values.values(), color='blue', label='Data')
    plt.plot(x_normalized, y_pred, color='red', label='Regression Line')
    plt.title(f'Linear regression {county_name} (2006-2015)', fontsize=14)
    plt.xlabel('Wildfires (Acres Burnt)')
    plt.ylabel('Shannon Index')
    plt.legend()
    if name != None:
        plt.savefig(f'plots/{name}.png')
        plt.close()
    else:
        print(f"Pearson Correlation Coefficient: {r:.4f}")
        print("p-value: ", p_value)
        print(f"Slope: {slope}, Intercept: {intercept}, R²: {r2}")
        plt.show()
        plt.close()
    return r, p_value, r2


# Plots linear regression results
def plot_linear_regression_results(r_values, p_values, r2_values, name=None):
    fig, axs = plt.subplots(1, 2, figsize=(16, 6))
    # Pearson Coefficient vs. p-value
    sns.scatterplot(
        ax=axs[0],
        x=r_values,
        y=p_values,
        hue=np.array(p_values) < 0.05,
        palette={True: 'red', False: 'blue'},
        legend="brief",
        s=100
    )
    axs[0].axhline(0.05, color='gray', linestyle='--', linewidth=1, label='p = 0.05')
    axs[0].set_title('Pearson Coefficient vs. p-value', fontsize=16)
    axs[0].set_xlabel('Pearson Coefficient', fontsize=14)
    axs[0].set_ylabel('p-value', fontsize=14)
    axs[0].set_xlim(-1, 1)
    axs[0].set_ylim(0, 1)
    axs[0].legend(title='Significant (p < 0.05)', loc='upper right')
    axs[0].grid(alpha=0.3)

    # R^2 vs. p-value
    sns.scatterplot(
        ax=axs[1],
        x=r2_values,
        y=p_values,
        hue=np.array(p_values) < 0.05,
        palette={True: 'red', False: 'blue'},
        legend=False,
        s=100
    )
    axs[1].axhline(0.05, color='gray', linestyle='--', linewidth=1, label='p = 0.05')
    axs[1].set_title('$R^2$ vs. p-value', fontsize=16)
    axs[1].set_xlabel('$R^2$', fontsize=14)
    axs[1].set_ylabel('p-value', fontsize=14)
    axs[1].set_xlim(0, 1)
    axs[1].set_ylim(0, 1)
    axs[1].grid(alpha=0.3)

    plt.tight_layout()

    if name is not None:
        plt.savefig(f'plots/{name}.png')
        plt.close(fig)
    else:
        plt.show()
        plt.close(fig)


# Extracts all fires from dataset of specific country between year1 and year2
def extract_fires_county_year(db_path, county, year1, year2):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT DISCOVERY_DATE, FIRE_SIZE
        FROM Fires
        WHERE COUNTY == {county}
        AND FIRE_YEAR between {year1} AND {year2};
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


# Extracts all fires for all counties between year1 and year2
def extract_fires_for_year(db_path, year1, year2):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT DISCOVERY_DATE, FIRE_SIZE
        FROM Fires
        WHERE STATE == 'CA'
        AND FIRE_YEAR BETWEEN {year1} AND {year2};
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


# Extracts all fires
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


# Plots fires
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
    plt.savefig('plots/fires.png')


# Plots fires and bird sightings together
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
    plt.savefig('plots/fires.png')

    plt.figure(figsize=(10, 6))

    plt.plot(dates_sightings, sightings_count, label='bird counts')

    plt.title('Bird sightings (2006-2015)', fontsize=14)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Count', fontsize=12)

    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=10)

    plt.tight_layout()
    plt.savefig('plots/sightings.png')


# Plots fires against shannon index values
def plot_shannon_fires(fires, shannon_values, name=None):
    dates_fires = list(fires.keys())
    fire_counts = list(fires.values())
    dates_shannon = list(shannon_values.keys())
    values_shannon = list(shannon_values.values())

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

    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.title('Amount of acres burnt in CA against shannon index (2006-2015)', fontsize=14)
    fig.tight_layout()
    if name != None:
        plt.savefig(f'plots/{name}.png')
    else:
        plt.show()
    plt.close()
