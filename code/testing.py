import datetime as dt
import sqlHandling, shannon_calculation, shannon_fires, population, lag


def state_wide_sIndex_vs_fires(file_path, fire_path):
    print("Start test 1: state wide Shannon index vs acres burnt...")
    fires = sqlHandling.extract_fires_for_year(fire_path, 2006, 2008)
    shannon_values = {}
    for year in range(2006,2009):
        for month in range(1,13):
            if year == 2008 and month > 10:
                break
            shannon_values[dt.date(year, month, 15)] = shannon_calculation.shannon_index_by_month(file_path, month, year)
    sqlHandling.plot_shannon_fires(fires, shannon_values, 't1_regular_index_vs_fires')


def state_wide_sIndex_decomposed_vs_fires(file_path, fire_path):
    print("Start test 2: Decompose state wide Shannon index and plot vs acres burnt...")
    fires = sqlHandling.extract_fires_for_year(fire_path, 2006, 2008)
    shannon_values = {}
    for year in range(2006,2009):
        for month in range(1,13):
            if year == 2008 and month > 10:
                break
            shannon_values[dt.date(year, month, 15)] = shannon_calculation.shannon_index_by_month(file_path, month, year)
    decomposed_values = shannon_calculation.shannon_fourier_decomposed(shannon_values)
    sqlHandling.plot_shannon_fires(fires, decomposed_values, 't2_decomposed_index_vs_fires')


def county_level_sIndex_decomposed_vs_fires(file_path, fire_path):
    print("Start test 3: Decompose county level Shannon index and plot vs acres burnt for each county...")
    fires = shannon_fires.extract_all_fires(fire_path)
    print(fires.keys())
    for county in shannon_fires.counties_standalone:
        print(f'Testing for {county}...')
        county_birds = shannon_fires.sort_county_by_date(file_path, 'ebird_counties_datesorted.txt', f'{county}')
        county_fires = fires[county.lower()]
        shannon_values = shannon_fires.shannon_index_by_day_for_array(county_birds)
        decomposed_values = shannon_calculation.shannon_fourier_decomposed(shannon_values)
        avg_values = lag.fit_shannon_to_months_avg(decomposed_values, True)
        sqlHandling.plot_shannon_fires(county_fires, avg_values, f't3_{county}')


def linear_regression_county_shannon(file_path, fire_path):
    print("Start test 4: Apply linear regression to each counties decomposed shannon index and fires...")
    r_values = []
    p_values = []
    r2_values = []
    fires = shannon_fires.extract_all_fires(fire_path)
    for county in shannon_fires.counties_standalone:
        print(f'Testing for {county}...')
        county_birds = shannon_fires.sort_county_by_date(file_path, 'ebird_counties_datesorted.txt', f'{county}')
        county_fires = fires[county.lower()]
        shannon_values = shannon_fires.shannon_index_by_day_for_array(county_birds)
        decomposed_values = shannon_calculation.shannon_fourier_decomposed(shannon_values)
        avg_values = lag.fit_shannon_to_months_avg(decomposed_values, True)
        r, p_value, r2 = sqlHandling.linear_regression_fires(county_fires, avg_values, name=f't4_{county}')
        r_values.append(r)
        p_values.append(p_value)
        r2_values.append(r2)
    sqlHandling.plot_linear_regression_results(r_values, p_values, r2_values)


def plot_5_biggest_fires_per_county(bird_path, fire_path):
    print("Plotting 5 biggest fires, linear regression and shannon values per county ")
    shannon_fires.plot_shannon_for_all_counties(bird_path, fire_path)


def population_numbers_county():
    pass


def linear_regression_county_population():
    pass


def lag_shannon_index():
    pass


def lag_population_numbers():
    pass


bird_path = 'data/trimmed_dataset.txt'
fire_path = 'data/trimmed_firedata.sqlite'
# state_wide_sIndex_vs_fires(bird_path, fire_path)
# state_wide_sIndex_decomposed_vs_fires(bird_path, fire_path)
# county_level_sIndex_decomposed_vs_fires(bird_path, fire_path)
linear_regression_county_shannon(bird_path, fire_path)
