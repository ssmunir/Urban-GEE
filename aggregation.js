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

// Step 4: Compute population density based on aggregated population
var area = ee.Image.pixelArea(); // Area in square meters
var density = population1km.divide(area).multiply(1e6); // Convert to people per km²

// Step 5: Aggregate data into density bins, including an open-ended last bin
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
                                geometry: region,
                                maxPixels: 1e13,
                                scale: 1000, // Match the dataset resolution
                              }).get('population_count');

  // Return the feature with bin info and both metrics
  return ee.Feature(null, {
    'density_bin': lowerBound,
    'total_population': binPopulation
  });
});

// Step 6: Convert to FeatureCollection for inspection
var aggregatedFC = ee.FeatureCollection(aggregatedData);
//print('Aggregated Population by Density Bins:', aggregatedFC);

// Optional: Export aggregated data for external analysis
Export.table.toDrive({
  collection: aggregatedFC,
  description: 'NigeriaPopulation1kmDensity',
  fileFormat: 'CSV'
});
