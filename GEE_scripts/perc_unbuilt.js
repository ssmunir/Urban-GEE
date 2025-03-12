/**** REVISED SCRIPT FOR REALISTIC UNBUILT PERCENTAGE DISTRIBUTION ****/
// Load datasets
var ghs = ee.Image('JRC/GHSL/P2023A/GHS_BUILT_S/2025').select('built_surface');
var countriesFC = ee.FeatureCollection('FAO/GAUL/2015/level0');
var nigeria = countriesFC.filter(ee.Filter.eq('ADM0_NAME', 'Nigeria')).geometry();

// Keep only pixels 0..10000, mask out anything else (like 65535)
var validMask = ghs.gte(0).and(ghs.lte(10000));
var ghsMasked = ghs.updateMask(validMask);

// Calculate percentage built in each 100m cell (0-100 scale)
var percentBuilt100m = ghsMasked.divide(100);

// Aggregate to 1km using average percentage
var avgPercentBuilt1km = percentBuilt100m
  .reduceResolution({
    reducer: ee.Reducer.mean(),
    bestEffort: true
  })
  .reproject({
    crs: ghsMasked.projection(),
    scale: 1000
  })
  .clip(nigeria);

// Calculate percentage unbuilt (0-100 scale)
var percentUnbuilt1km = ee.Image.constant(100).subtract(avgPercentBuilt1km);

// Round to nearest whole percentage for more intuitive grouping
var roundedPercentUnbuilt = percentUnbuilt1km.round();

// Get frequency histogram
var histDict = roundedPercentUnbuilt.reduceRegion({
  reducer: ee.Reducer.frequencyHistogram(),
  geometry: nigeria,
  scale: 1000,
  bestEffort: true,
  maxPixels: 1e9,
  tileScale: 4
});

// Extract frequency dictionary
var bandName = roundedPercentUnbuilt.bandNames().get(0);
var freqDict = ee.Dictionary(histDict.get(bandName));

// Print for debugging
print('Number of unique unbuilt percentage values:', freqDict.size());
print('Sample of frequency dictionary:', freqDict);

// Convert to Feature Collection
var keys = freqDict.keys().sort();
var feats = keys.map(function(k) {
  var percentUnbuiltValue = ee.Number.parse(k);
  var count = ee.Number(freqDict.get(k));
  return ee.Feature(null, {
    percent_unbuilt: percentUnbuiltValue,
    frequency: count
  });
});
var freqFC = ee.FeatureCollection(feats);

// Export the table
Export.table.toDrive({
  collection: freqFC,
  description: 'Nigeria_1km_Percent_Unbuilt_Revised',
  fileFormat: 'CSV',
  selectors: ['percent_unbuilt', 'frequency']
});

