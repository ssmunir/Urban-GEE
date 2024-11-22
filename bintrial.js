// Step 1: Import GHS-POP data and country boundaries
// Load population data for 2020
var ghsPop2020 = ee.Image("JRC/GHSL/P2023A/GHS_POP/2020");
var countries = ee.FeatureCollection('FAO/GAUL/2015/level0');

// Step 2: Filter for Nigeria and clip the population data
var nigeria = countries.filter(ee.Filter.eq('ADM0_NAME', 'Nigeria'));
var region = nigeria.geometry();
var population = ghsPop2020.clip(region);

var proj_0 = population.projection();

// Aggregate population data to 1-km grid cells
var proj_at1km = proj_0.atScale(1000);

var population1km = population.reduceResolution({
    reducer: ee.Reducer.sum().unweighted(),
    maxPixels: 1024
    })
    // Request the data at the 1sqkm scale and projection of the image.
    .reproject({
    crs: proj_at1km
});


// Create a new raster by rounding up population values to the nearest 100
var roundedRaster = population1km.expression(
  "ceil(pop / 100) * 100", {
    'pop': population1km
  }
).rename('rounded_population');


print(roundedRaster.projection())
//Map.addLayer(roundedRaster, {}, 'rr')

var pp = population1km.addBands(roundedRaster);
//Map.addLayer(pp, {}, 'mergedpop');

var popByBin = population1km.addBands(roundedRaster).reduceRegion({
  reducer: ee.Reducer.sum().group({
    groupField: 1
    }),
  geometry: region,
  scale: 1000,
  maxPixels: 1e9
});

print(popByBin);

// Extract the grouped data from popByBin
var groups = ee.List(ee.Dictionary(popByBin).get('groups'));

// Compute the total population across all bins
var totalPopulation = groups.map(function(group) {
  var value = ee.Dictionary(group).get('sum'); // Extract the sum for each group
  return ee.Number(value); // Ensure it's treated as a number
}).reduce(ee.Reducer.sum());

// Print the total population
print('Total Population Across All Bins:', totalPopulation);


// Convert the groups list to a FeatureCollection for export
var features = groups.map(function(group) {
  group = ee.Dictionary(group); // Cast each group as a dictionary
  return ee.Feature(null, {
    'Bin': group.get('group'), // Bin ID
    'PopulationSum': group.get('sum') // Population sum for the bin
  });
});

// Create a FeatureCollection
var featureCollection = ee.FeatureCollection(features);

// Export the FeatureCollection as a CSV file
Export.table.toDrive({
  collection: featureCollection,
  description: 'PopulationByBin',
  fileFormat: 'CSV',
  selectors: ['Bin', 'PopulationSum'] // Columns to include
});


