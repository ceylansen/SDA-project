import datetime as dt
import sqlHandling, shannon_calculation, shannon_fires, population, lag
from scipy.ndimage import gaussian_filter1d


# Test 1: Plots the state wide shannon index against the forest fires in the whole state
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


# Test 2: Plots the state wide decomposed shannon index fluctuations against the forest
# fires in the whole state
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


# Test 3
def county_level_sIndex_decomposed_vs_fires(file_path, fire_path):
    print("Start test 3: Decompose county level Shannon index and plot vs acres burnt for each county...")
    fires = shannon_fires.extract_all_fires(fire_path)
    for county in shannon_fires.counties_standalone:
        print(f'Testing for {county}...')
        county_birds = shannon_fires.sort_county_by_date(file_path, f'{county}')
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
        county_birds = shannon_fires.sort_county_by_date(file_path, f'{county}')
        county_fires = fires[county.lower()]
        shannon_values = shannon_fires.shannon_index_by_day_for_array(county_birds)
        decomposed_values = shannon_calculation.shannon_fourier_decomposed(shannon_values)
        avg_values = lag.fit_shannon_to_months_avg(decomposed_values, True)
        avg_fires = lag.fit_fires_to_months(county_fires, True)
        avg_values, avg_fires = lag.equalize_dicts(avg_values, avg_fires)
        r, p_value, r2 = sqlHandling.linear_regression_fires(avg_fires, avg_values, name=f't4_{county}')
        r_values.append(r)
        p_values.append(p_value)
        r2_values.append(r2)
    sqlHandling.plot_linear_regression_results(r_values, p_values, r2_values, 't4_all_results')


def plot_5_biggest_fires_per_county(bird_path, fire_path):
    print("Plotting 5 biggest fires, linear regression and shannon values per county ")
    shannon_fires.plot_shannon_for_all_counties(fire_path, bird_path)


def population_numbers_county(file_path, fire_path):
    print("Start test 5: Decompose county level bird sightings and plot vs acres burnt for each county...")
    fires = shannon_fires.extract_all_fires(fire_path)
    for county in shannon_fires.counties_standalone:
        print(f'Testing for {county}...')
        population.plot_population_fires_county(file_path, fire_path, county, f't5_{county}')


def linear_regression_county_population(file_path):
    print("Start test 6: Linear regression bird sightings")
    r_values = []
    p_values = []
    r2_values = []
    for county in shannon_fires.counties_standalone:
        print(f'Testing for {county}...')
        r, p_value, r2 = population.plot_population_fires_county(file_path, fire_path, county, f't6_{county}', True)
        r_values.append(r)
        p_values.append(p_value)
        r2_values.append(r2)
    sqlHandling.plot_linear_regression_results(r_values, p_values, r2_values, 't6_all_results')


def lag_shannon_index(file_path, fire_path):
    print("Start test 7: Lag of shannon index")
    fires = shannon_fires.extract_all_fires(fire_path)
    best_lags = []
    best_correlations = []
    for county in shannon_fires.counties_standalone:
        county_birds = shannon_fires.sort_county_by_date(file_path, f'{county}')
        shannon_values = shannon_fires.shannon_index_by_day_for_array(county_birds)
        month_avgs = lag.fit_shannon_to_months_avg(shannon_values, True)
        decomposed_values = shannon_calculation.shannon_fourier_decomposed(month_avgs)
        monthly_fires = lag.fit_fires_to_months(fires[county.lower()])
        best_lag, best_correlation = lag.cross_correlate(decomposed_values, monthly_fires)
        best_lags.append(best_lag)
        best_correlations.append(best_correlation)
    lag.plot_lag_results(best_lags, best_correlations, f't7_results')


def lag_population_numbers(file_path, fire_path):
    print("Start test 8: Lag of bird sightings")
    fires = shannon_fires.extract_all_fires(fire_path)
    best_lags = []
    best_correlations = []
    for county in shannon_fires.counties_standalone:
        total_observations = population.count_total_bird_population_by_county(county, file_path)
        weights = population.adjust_for_userbase(county, 'data/filtered_effort_sample.txt')
        weighted_observations = { date: count * weights.get(date.year, 1) for date, count in total_observations.items()}
        month_avgs = lag.fit_shannon_to_months_avg(weighted_observations)
        decomposed_values = shannon_calculation.shannon_fourier_decomposed(month_avgs)
        monthly_fires = lag.fit_fires_to_months(fires[county.lower()])
        best_lag, best_correlation = lag.cross_correlate(decomposed_values, monthly_fires)
        best_lags.append(best_lag)
        best_correlations.append(best_correlation)
    lag.plot_lag_results(best_lags, best_correlations, f't8_results')


bird_path = 'data/trimmed_dataset.txt'
fire_path = 'data/trimmed_firedata.sqlite'
# state_wide_sIndex_vs_fires(bird_path, fire_path)
# state_wide_sIndex_decomposed_vs_fires(bird_path, fire_path)
# county_level_sIndex_decomposed_vs_fires(bird_path, fire_path)
# linear_regression_county_shannon(bird_path, fire_path)
# population_numbers_county(bird_path, fire_path)
# lag_shannon_index(bird_path, fire_path)
# lag_population_numbers(bird_path, fire_path)
plot_5_biggest_fires_per_county(bird_path, fire_path)
