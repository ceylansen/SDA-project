import sqlite3
import matplotlib.pyplot as plt
import datetime as dt

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


db_path = 'data/firedata.sqlite'
fires = extract_fires(db_path)
max_fires = max(zip(fires.values(), fires.keys()))
print("Date with the largest fire:", max_fires)

plot_fires(fires)
