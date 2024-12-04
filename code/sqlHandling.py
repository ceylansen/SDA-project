import sqlite3

db_path = 'data/FPA_FOD_20170508.sqlite'

# sql_file_path = 'boundingbox.sql'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# with open(sql_file_path, 'r') as sql_file:
#     sql = sql_file.read()

# cursor.executescript(sql)

# conn.commit()

# code voor de bounding box van de hele land bird monitoring data set 2007-2017
cursor.execute(
    """
    SELECT FIRE_YEAR, DISCOVERY_DATE, FIRE_SIZE
    FROM Fires
    WHERE LATITUDE BETWEEN 38.6703 AND 39.6335
    AND LONGITUDE BETWEEN -78.7646 AND -76.7983
    AND FIRE_YEAR BETWEEN 2007 AND 2015;
    """
    )
rows = cursor.fetchall()
# print(len(rows))
for row in rows:
    print(row[0], row[1], row[2])

conn.close()