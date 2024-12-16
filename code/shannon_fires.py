import sqlite3
import matplotlib.pyplot as plt
import datetime as dt
import random
import json
from collections import Counter
import math
import shannon_calculation
from time import sleep

countytocode = {
    "alameda": "1",
    "alpine": "3",
    "amador": "5",
    "butte": "7",
    "calaveras": "9",
    "colusa": "11",
    "contra costa": "13",
    "del norte": "15",
    "el Dorado": "17",
    "fresno": "19",
    "glenn": "21",
    "humboldt": "23",
    "imperial": "25",
    "inyo": "27",
    "kern": "29",
    "kings": "31",
    "lake": "33",
    "lassen": "35",
    "los Angeles": "37",
    "madera": "39",
    "marin": "41",
    "mariposa": "43",
    "mendocino": "45",
    "merced": "47",
    "mdoc": "49",
    "mono": "51",
    "monterey": "53",
    "napa": "55",
    "nevada": "57",
    "orange": "59",
    "placer": "61",
    "plumas": "63",
    "riverside": "65",
    "sacramento": "67",
    "san benito": "69",
    "san bernardino": "71",
    "san diego": "73",
    "san francisco": "75",
    "san joaquin": "77",
    "san luis Obispo": "79",
    "san mateo": "81",
    "santa barbara": "83",
    "santa clara": "85",
    "santa cruz": "87",
    "shasta": "89",
    "sierra": "91",
    "siskiyou": "93",
    "solano": "95",
    "sonoma": "97",
    "stanislaus": "99",
    "sutter": "101",
    "tehama": "103",
    "trinity": "105",
    "tulare": "107",
    "tuolumne": "109",
    "ventura": "111",
    "yolo": "113",
    "yuba": "115"
}

codetocounty = {
    "1": "alameda",
    "3": "alpine",
    "5": "amador",
    "7": "butte",
    "9": "calaveras",
    "11": "colusa",
    "13": "contra costa",
    "15": "del norte",
    "17": "el dorado",
    "19": "fresno",
    "21": "glenn",
    "23": "humboldt",
    "25": "imperial",
    "27": "inyo",
    "29": "kern",
    "31": "kings",
    "33": "lake",
    "35": "lassen",
    "37": "los angeles",
    "39": "madera",
    "41": "marin",
    "43": "mariposa",
    "45": "mendocino",
    "47": "merced",
    "49": "modoc",
    "51": "mono",
    "53": "monterey",
    "55": "napa",
    "57": "nevada",
    "59": "orange",
    "61": "placer",
    "63": "plumas",
    "65": "riverside",
    "67": "sacramento",
    "69": "san benito",
    "71": "san bernardino",
    "73": "san diego",
    "75": "san francisco",
    "77": "san joaquin",
    "79": "san luis obispo",
    "81": "san mateo",
    "83": "santa barbara",
    "85": "santa clara",
    "87": "santa cruz",
    "89": "shasta",
    "91": "sierra",
    "93": "siskiyou",
    "95": "solano",
    "97": "sonoma",
    "99": "stanislaus",
    "101": "sutter",
    "103": "tehama",
    "105": "trinity",
    "107": "tulare",
    "109": "tuolumne",
    "111": "ventura",
    "113": "yolo",
    "115": "yuba"
}


DAYSPOSTFIRE = 365

def get_largest_fires(fires, county):
    largest_fires = sorted(fires.items(), key=lambda x: x[1], reverse=True)[:5]
    dates, sizes = zip(*largest_fires)
    return dates, sizes

def shannon_index_by_month_filtered(filtered_bird_data, month, year):
    species_counts = Counter()

    for row in filtered_bird_data:
        columns = row.split('\t')  # Split the line into columns
        date = columns[0]  # OBSERVATION DATE
        common_name = columns[1].strip()  # COMMON NAME

        y, m, d = date.split('-')
        if year == int(y) and month == int(m):
            species_counts[common_name] += 1
        elif int(y) > year:
            break

    total_sightings = sum(species_counts.values())
    shannon_index = 0
    for count in species_counts.values():
        p_i = count / total_sightings
        shannon_index -= p_i * math.log(p_i)
    return shannon_index

def get_real_date(julian_day):
    julian_base = 1721424.5  # Julian Day 0 blijkbaar
    gregorian_ordinal = int(julian_day - julian_base)
    return dt.date.fromordinal(gregorian_ordinal)


def extract_all_fires(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
    SELECT DISCOVERY_DATE, FIRE_SIZE, COUNTY
    FROM Fires
    WHERE STATE = 'CA'
    AND FIRE_YEAR BETWEEN 2006 AND 2015;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    fires = {}
    for julian_date, fire_size, county in rows:
        try:
            gregorian_date = get_real_date(julian_date)
            if county:
                county = county.strip().lower()
                is_county_code = county.isdigit()
                if is_county_code:
                    county = codetocounty.get(county, "")
            else:
                continue
            if county not in fires:
                fires[county] = {}
            if gregorian_date not in fires[county]:
                fires[county][gregorian_date] = fire_size
            else:
                fires[county][gregorian_date] += fire_size
        except ValueError as e:
            print(f"Error converting Julian date {julian_date}: {e}")

    sorted_fires = {
        county: dict(sorted(dates.items()))
        for county, dates in fires.items()
    }

    with open("california_fires.json", "w") as file:
        json.dump(
            {
                county: {date.isoformat(): size for date, size in dates.items()}
                for county, dates in sorted_fires.items()
            },
            file,
        )

    return sorted_fires

def process_and_plot_for_county(county_name, fire_data, filtered_bird_data):
    fires = fire_data.get(county_name, {})
    if not fires:
        print(f"No fire data available for {county_name}. Skipping...")
        return

    dates, sizes = get_largest_fires(fires, county_name)

    shannon_values = {}
    years = list(range(2006, 2016))
    months = list(range(1, 13))
    for year in years:
        for month in months:
            shannon_values[dt.date(year, month, 15)] = shannon_index_by_month_filtered(
                filtered_bird_data, month, year
            )
    decomposed_values = shannon_calculation.shannon_fourier_decomposed(shannon_values)
    plot_shannon_test(dates, decomposed_values, fires, county_name)


def plot_shannon_for_all_counties(fire_data, bird_data_path):
    for county_name in fire_data:
        print(f"Processing county: {county_name}...")

        is_county_code = county_name.isdigit()

        try:
            with open(bird_data_path, 'r') as file:
                filtered_bird_data = []

                for line in file.readlines():
                    line = line.strip()
                    parts = line.split('\t')

                    if len(parts) < 4:
                        continue

                    bird_county = parts[2].strip().lower()
                    bird_county_code = parts[3].strip()
                    if bird_county_code.startswith("US-CA-"):
                        bird_county_code = bird_county_code.split("-")[-1]

                    if is_county_code:
                        county_code_padded = f"{int(county_name):03d}"
                        bird_county_code_padded = bird_county_code

                        if bird_county_code_padded == county_code_padded:
                            filtered_bird_data.append(line)
                    else:
                        if county_name.lower() in bird_county:
                            filtered_bird_data.append(line)

            if filtered_bird_data:
                process_and_plot_for_county(county_name, fire_data, filtered_bird_data)
            else:
                print(f"No bird data found for {county_name}.")

        except Exception as e:
            print(f"Failed to process {county_name}: {e}")

def plot_shannon_test(dates, shannon_values, fires, county_name):
    shannon_dates = list(shannon_values.keys())
    FIRE_MARGIN = 30

    fig, axs = plt.subplots(3, 2, figsize=(12, 10))
    axs = axs.flatten()

    for i, fire_date in enumerate(dates):
        fire_date_dt = fire_date
        start_date = fire_date_dt - dt.timedelta(days=FIRE_MARGIN)
        end_date = fire_date_dt + dt.timedelta(days=DAYSPOSTFIRE)

        filtered_dates = [d for d in shannon_dates if start_date <= d <= end_date]
        filtered_values = [shannon_values[d] for d in filtered_dates]

        surrounding_dates = [d for d in fires.keys() if start_date <= d <= end_date]
        surrounding_sizes = [fires[d] for d in surrounding_dates]

        axs[i].plot(filtered_dates, filtered_values, label="Shannon Index", color="blue")
        axs[i].set_title(f"{county_name.capitalize()} Fire {i+1} ({fire_date})")
        axs[i].set_xlabel("Date")
        axs[i].set_ylabel("Shannon Index", color="blue")
        axs[i].tick_params(axis="y", labelcolor="blue")

        axs[i].axvline(fire_date, color="red", linestyle="--", label="Largest Burn Day")

        ax2 = axs[i].twinx()
        ax2.bar(surrounding_dates, surrounding_sizes, color="orange", alpha=0.6, label="Acres Burned", width=3.0)
        ax2.set_ylabel("Acres Burned", color="orange")
        ax2.tick_params(axis="y", labelcolor="orange")

        axs[i].legend(loc="upper left")
        ax2.legend(loc="upper right")

    random_date = random.choice([d for d in shannon_dates if d <= max(shannon_dates) - dt.timedelta(days=DAYSPOSTFIRE)])
    start_date = random_date - dt.timedelta(days=FIRE_MARGIN)
    end_date = random_date + dt.timedelta(days=DAYSPOSTFIRE)

    filtered_dates = [d for d in shannon_dates if start_date <= d <= end_date]
    filtered_values = [shannon_values[d] for d in filtered_dates]

    axs[5].plot(filtered_dates, filtered_values, label="Shannon Index", color="blue")
    axs[5].set_title(f"Shannon Index after Random Date ({random_date})")
    axs[5].set_xlabel("Date")
    axs[5].set_ylabel("Shannon Index", color="blue")
    axs[5].tick_params(axis="y", labelcolor="blue")

    axs[5].legend()

    plt.tight_layout()
    plt.savefig(f"shannon_{county_name}.png")
    plt.close(fig)

db_path = "data/firedata.sqlite"
bird_path = "data/filtered_for_counties.txt"
fires = extract_all_fires(db_path)

plot_shannon_for_all_counties(fires, bird_path)

# dates, sizes = get_largest_fires(fires, county)
# shannon_values = {}
# years = list(range(2006, 2016))
# months = list(range(1, 13))
# for year in years:
#     for month in months:
#         shannon_values[dt.date(year, month, 15)] = shannon_calculation.shannon_index_by_month(bird_path, month, year)
# decomposed_values = shannon_calculation.shannon_fourier_decomposed(shannon_values)
# plot_shannon_test(dates, decomposed_values, fires)
