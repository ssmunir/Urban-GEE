// Step 1: Import GHS-POP data and country boundaries
// Load population data for 2020
var ghsPop2020 = ee.Image("JRC/GHSL/P2023A/GHS_POP/2020");
var countries = ee.FeatureCollection('FAO/GAUL/2015/level0');

// Import the CSV file as a FeatureCollection (uploaded to GEE)
var table = ee.FeatureCollection("projects/urbanization-436918/assets/region");
// Step 2: Add region information to countries

// Extract economy names from the regions CSV
var economyNames = table.select('Economy');

// Merge by country name
var countriesWithRegions = countries.map(function(country) {
  var countryName = country.get('ADM0_NAME'); // Get country name from the countries dataset
  var regionMatch = table.filter(ee.Filter.eq('Economy', countryName)).first(); // Match using Economy column
  var region = ee.Algorithms.If(regionMatch, regionMatch.get('Region'), 'Unknown'); // Extract Region or assign Unknown
  return country.set('Region', region); // Add the Region column to the countries dataset
});


//  Filter for North America region
var northAmerica = countriesWithRegions.filter(ee.Filter.eq('Region', 'North America'));

//  Process North America region
var regionGeometry = northAmerica.geometry(); // Merge geometries of North America

// Clip population data to North America
var population = ghsPop2020.clip(regionGeometry);

// Project population data to 1-km grid cells
var proj_0 = population.projection();
var proj_at1km = proj_0.atScale(1000);

var population1km = population.reduceResolution({
    reducer: ee.Reducer.sum().unweighted(),
    maxPixels: 1024
  })
  .reproject({
    crs: proj_at1km
  });

// Compute population density based on aggregated population
var area = ee.Image.pixelArea(); // Area in square meters
var density = population1km.divide(area).multiply(1e6); // Convert to people per km²

//  Aggregate data into density bins
var bins = ee.List.sequence(0, 29900, 100); // Closed bins up to 29,900
bins = bins.add(30000); // Add the open-ended last bin

var aggregatedData = bins.map(function(bin) {
  var lowerBound = ee.Number(bin);

  // Determine if it's the last bin
  var isLastBin = lowerBound.eq(30000);

  // Set the mask conditionally for the last bin
  var binMask = ee.Algorithms.If(
    isLastBin,
    density.gte(lowerBound), // Open-ended last bin: densities >= 30,000
    density.gt(lowerBound).and(density.lte(lowerBound.add(100))) // Regular bin
  );

  // Calculate total population in the bin
  var binPopulation = density.updateMask(binMask)
                              .reduceRegion({
                                reducer: ee.Reducer.sum(),
                                geometry: regionGeometry,
                                maxPixels: 1e13,
                                scale: 1000, // Match the dataset resolution
                              }).get('population_count');

  // Return the feature with bin info and total population
  return ee.Feature(null, {
    'region': 'North America',
    'density_bin': lowerBound,
    'total_population': binPopulation
  });
});

// Convert to FeatureCollection for inspection
var aggregatedFC = ee.FeatureCollection(aggregatedData);
//print("Aggregated Population Density for North America:", aggregatedFC);

// Export the results
Export.table.toDrive({
  collection: aggregatedFC,
  description: 'NorthAmericaPopulationDensityBins',
  fileFormat: 'CSV'
});