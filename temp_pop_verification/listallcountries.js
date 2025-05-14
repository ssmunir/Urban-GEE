// Import the FAO country boundaries feature collection
var countries = ee.FeatureCollection('FAO/GAUL/2015/level0');

// Get a list of all country names
var countryNames = countries.aggregate_array('ADM0_NAME');

// Sort the country names alphabetically for easier reference
var sortedCountryNames = countryNames.sort();

// Print the total number of countries
print('Total number of countries in FAO/GAUL/2015/level0:', countries.size());

// Print the sorted list of all country names
print('All countries (alphabetically):', sortedCountryNames);
