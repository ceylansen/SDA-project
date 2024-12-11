import sqlite3
import matplotlib.pyplot as plt
import datetime as dt

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

def get_real_date(julian_day):
    julian_base = 1721424.5  # Julian Day 0 blijkbaar
    gregorian_ordinal = int(julian_day - julian_base)
    return dt.date.fromordinal(gregorian_ordinal)


def extract_fires(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT DISCOVERY_DATE, FIRE_SIZE
        FROM Fires
        WHERE STATE = 'CA'
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


db_path = 'data/firedata.sqlite'
fires = extract_fires(db_path)
max_fires = max(zip(fires.values(), fires.keys()))
file_path_sightings = 'data/ebd_2006_2015.txt'
print("Date with the largest fire:", max_fires)

# plot_fires(fires)
# plot_fires_sightings(fires, ebirddatareader.sightings_per_date(file_path_sightings))
shannon_values = shannon_calculation.shannon_index_by_month_CA()
decomposed_values = shannon_calculation.shannon_fourier_decomposed(shannon_values)
# print(shannon_values)
plot_shannon_fires(fires, decomposed_values)