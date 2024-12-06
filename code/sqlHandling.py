import sqlite3
import matplotlib.pyplot as plt

def extract_fireYear(date):
    db_path = 'data/FPA_FOD_20170508.sqlite'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
            f"""
            SELECT FIRE_YEAR, DISCOVERY_DATE, FIRE_SIZE
            FROM Fires
            WHERE DISCOVERY_DATE = {date};
            """
            )
    rows = cursor.fetchall()
    conn.close()
    return rows

def extract_fires():
    db_path = 'data/FPA_FOD_20170508.sqlite'

    # sql_file_path = 'boundingbox.sql'

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # with open(sql_file_path, 'r') as sql_file:
    #     sql = sql_file.read()

    # cursor.executescript(sql)

    # conn.commit()

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
    fires = {}
    # for i in range(1, 9):
        # cursor.execute(
        #     f"""
        #     SELECT FIRE_YEAR, DISCOVERY_DATE, FIRE_SIZE, STATE
        #     FROM Fires
        #     WHERE STATE = 'CA'
        #     AND FIRE_YEAR = {2007 + i};
        #     """
        #     )
    cursor.execute(
        f"""
        SELECT DISCOVERY_DATE, FIRE_SIZE
        FROM Fires
        WHERE STATE = 'CA'
        AND FIRE_YEAR BETWEEN 2006 AND 2015;
        """
        )
    rows = cursor.fetchall()
    biggest_fire = 0
    for row in rows:
        # print(row[1])
        if fires.get(row[0], False) == False:
            fires[row[0]] = row[1]
        else:
            fires[row[0]] += row[1]
        if biggest_fire < row[1]:
            biggest_fire = row[1]
    print("biggest fire: ", biggest_fire)
    # for row in rows:
    #     print(row[0], row[1], row[2], row[3])

    # Close the connection
    conn.close()
    sorted_fires = dict(sorted(fires.items()))
    return sorted_fires

def plot_fires(fires):
    # Extract years and fire counts from the dictionary
    dates = list(fires.keys())
    fire_counts = list(fires.values())

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(dates, fire_counts, linestyle='-', label='Number of Fires')

    # Add labels and title
    plt.title('Number of Fires in California (2008-2015)', fontsize=14)
    plt.xlabel('Julian Date', fontsize=12)
    plt.ylabel('Acres burnt', fontsize=12)

    # Add grid and legend
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=10)

    # Show the plot
    plt.tight_layout()
    plt.show()

fires = extract_fires()
max_fires = max(zip(fires.values(), fires.keys()))
print(max_fires)
# print(extract_fireYear(2450000)[0][0])
plot_fires(fires)