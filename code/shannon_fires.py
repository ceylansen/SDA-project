import sqlite3
import matplotlib.pyplot as plt
import datetime as dt
import random
import json
from collections import Counter
import math
import shannon_calculation

countytocode = {
    "Alameda": "1",
    "Alpine": "3",
    "Amador": "5",
    "Butte": "7",
    "Calaveras": "9",
    "Colusa": "11",
    "Contra Costa": "13",
    "Del Norte": "15",
    "El Dorado": "17",
    "Fresno": "19",
    "Glenn": "21",
    "Humboldt": "23",
    "Imperial": "25",
    "Inyo": "27",
    "Kern": "29",
    "Kings": "31",
    "Lake": "33",
    "Lassen": "35",
    "Los Angeles": "37",
    "Madera": "39",
    "Marin": "41",
    "Mariposa": "43",
    "Mendocino": "45",
    "Merced": "47",
    "Modoc": "49",
    "Mono": "51",
    "Monterey": "53",
    "Napa": "55",
    "Nevada": "57",
    "Orange": "59",
    "Placer": "61",
    "Plumas": "63",
    "Riverside": "65",
    "Sacramento": "67",
    "San Benito": "69",
    "San Bernardino": "71",
    "San Diego": "73",
    "San Francisco": "75",
    "San Joaquin": "77",
    "San Luis Obispo": "79",
    "San Mateo": "81",
    "Santa Barbara": "83",
    "Santa Clara": "85",
    "Santa Cruz": "87",
    "Shasta": "89",
    "Sierra": "91",
    "Siskiyou": "93",
    "Solano": "95",
    "Sonoma": "97",
    "Stanislaus": "99",
    "Sutter": "101",
    "Tehama": "103",
    "Trinity": "105",
    "Tulare": "107",
    "Tuolumne": "109",
    "Ventura": "111",
    "Yolo": "113",
    "Yuba": "115"
}

codetocounty = {
    "1": "Alameda",
    "3": "Alpine",
    "5": "Amador",
    "7": "Butte",
    "9": "Calaveras",
    "11": "Colusa",
    "13": "Contra Costa",
    "15": "Del Norte",
    "17": "El Dorado",
    "19": "Fresno",
    "21": "Glenn",
    "23": "Humboldt",
    "25": "Imperial",
    "27": "Inyo",
    "29": "Kern",
    "31": "Kings",
    "33": "Lake",
    "35": "Lassen",
    "37": "Los Angeles",
    "39": "Madera",
    "41": "Marin",
    "43": "Mariposa",
    "45": "Mendocino",
    "47": "Merced",
    "49": "Modoc",
    "51": "Mono",
    "53": "Monterey",
    "55": "Napa",
    "57": "Nevada",
    "59": "Orange",
    "61": "Placer",
    "63": "Plumas",
    "65": "Riverside",
    "67": "Sacramento",
    "69": "San Benito",
    "71": "San Bernardino",
    "73": "San Diego",
    "75": "San Francisco",
    "77": "San Joaquin",
    "79": "San Luis Obispo",
    "81": "San Mateo",
    "83": "Santa Barbara",
    "85": "Santa Clara",
    "87": "Santa Cruz",
    "89": "Shasta",
    "91": "Sierra",
    "93": "Siskiyou",
    "95": "Solano",
    "97": "Sonoma",
    "99": "Stanislaus",
    "101": "Sutter",
    "103": "Tehama",
    "105": "Trinity",
    "107": "Tulare",
    "109": "Tuolumne",
    "111": "Ventura",
    "113": "Yolo",
    "115": "Yuba"
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


def combine_fire_data(fire_data, county_name, county_code):
    combined_data = {}

    if county_name in fire_data:
        combined_data[county_name] = fire_data[county_name]

    if county_code in fire_data:
        if county_name not in combined_data:
            combined_data[county_name] = fire_data[county_code]
        else:
            for date, size in fire_data[county_code].items():
                if date in combined_data[county_name]:
                    combined_data[county_name][date] += size
                else:
                    combined_data[county_name][date] = size

    return combined_data


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
    WHERE STATE = 'CA';
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
                combined_data = combine_fire_data(fire_data, county_name, codetocounty.get(county_name, ""))
                process_and_plot_for_county(county_name, combined_data, filtered_bird_data)
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
