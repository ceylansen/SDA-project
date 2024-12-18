import datetime as dt
import sqlHandling, shannon_calculation, shannon_fires, population, lag

def state_wide_sIndex_vs_fires(file_path, fire_path):
    print("Start test 1: state wide Shannon index vs acres burnt...")
    fires = sqlHandling.extract_fires_for_year(fire_path, 2006)
    shannon_values = {}
    for month in range(1,13):
        shannon_values[dt.date(2006, month, 15)] = shannon_calculation.shannon_index_by_month(file_path, month, 2006)
    sqlHandling.plot_shannon_fires(fires, shannon_values, 't1_regular_index_vs_fires')
    return


def state_wide_sIndex_decomposed_vs_fires(file_path, fire_path):
    print("Start test 2: Decompose state wide Shannon index and plot vs acres burnt...")
    fires = sqlHandling.extract_fires_for_year(fire_path, 2006)
    shannon_values = {}
    for month in range(1,13):
        shannon_values[dt.date(2006, month, 15)] = shannon_calculation.shannon_index_by_month(file_path, month, 2006)
    decomposed_values = shannon_calculation.shannon_fourier_decomposed(shannon_values)
    sqlHandling.plot_shannon_fires(fires, decomposed_values, 't2_decomposed_index_vs_fires')
    return


def county_level_sIndex_decomposed_vs_fires(file_path, fire_path):
    for county in shannon_fires.countytocode:
        print("Start test 3: Decompose county level Shannon index and plot vs acres burnt for each county...")
        fires = sqlHandling.extract_fires_county_year(fire_path, county, 2006)
        shannon_values = {}
        for month in range(1,13):
            shannon_values[dt.date(2006, month, 15)] = shannon_calculation.shannon_index_by_month(file_path, month, 2006)
        decomposed_values = shannon_calculation.shannon_fourier_decomposed(shannon_values)
        sqlHandling.plot_shannon_fires(fires, decomposed_values, f't3_{county}')
    return


def plot_5_biggest_fires_per_county():
    # ceylan
    pass


bird_path = 'data/ebd_2006_2015.txt'
fire_path = 'data/firedata.sqlite'
shannon_calculation.filter_for_county(bird_path, list([2006,2007,2008]))
# state_wide_sIndex_vs_fires(bird_path, fire_path)
# state_wide_sIndex_decomposed_vs_fires(bird_path, fire_path)
