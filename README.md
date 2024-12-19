# SDA-project-

Structure of plots, there are folders for different tests performed on either counties within a state or the whole state itself (California)

The folders contain different plots here is a short description for them

Shannon_values_per_county_plots: The shannon index plotted from 2006 to 2015 by month for every county in California

Shannon_5_fires_test_per_county_plots: 5 plots of a certain period of the shannon index plotted after the day of the largest amount of acres burned by wildfire from 2006 to 2015, and a 6th plot from a random date and the period after that plotted for all counties.

regression_per_county_plots: Plots of the linear regression between the shannon index and acres burnt by wilfdires normalized.

California_plots: Contains a mix of all of the above with some added self-explanatory plots contained in the same folder for the whole state


# To test the code run testing.py in the following way: python testing.py <test_number>. The tests are using a small sample of our very large original dataset

Test 1: Plots the state wide shannon index against the forest fires in the whole state
Test 2: Plots the state wide decomposed shannon index fluctuations against the forest fires in the whole state
Test 3: plots the decomposed shannon index for each county against its respective forest fires
Test 4: Apply linear regression to each shannon index plot of every county
Test 5: Takes the 5 biggest fires in each county and plots it together with a random fire and their respective shannon indeces
Test 6: Plots the weighted total bird sightings for each month in each state against that states's fires
Test 7: Applies linear regression to the weighted bird sightings and the fires
Test 8: Computes the best lag and the corresponding correlation for each county's shannon index using cross correlation
Test 9: Computes the best lag and the corresponding correlation for each county's weighted sightings using cross correlation

Each test saves the graphs in the plots folder.

# NOTE: Some tests do still take around 2 minutes or so to complete, however, for tests 3, 5 and 6 you can end prematurely since they save each graph after finishing a state, so you do not have to wait for every state to finish. They should all be manageable from our testing.


Libraries used one might not already have:
sqlite3
statsmodels
csv
scipy
sklearn
