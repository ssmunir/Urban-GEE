//See notes: https://spatialthoughts.com/2021/05/13/aggregating-population-data-gee/

// Load country boundaries and population raster
var countries = ee.FeatureCollection('FAO/GAUL/2015/level0');
var pop2020 = ee.Image('JRC/GHSL/P2023A/GHS_POP/2020');

// Mask out negative values
var popClean = pop2020.updateMask(pop2020.gte(0));

// Select country of interest
var countryname = 'Canada';
var country = countries.filter(ee.Filter.eq('ADM0_NAME', countryname)).first();

print('Working on country: ', countryname);
print('Native projection of pop raster: ', pop2020.projection().getInfo());

// Check band names
print('Population image bands:', popClean.bandNames());

// Select the correct band (first band)
var popBand = popClean.select(0);

// Get native projection and scale
var nativeProj = popBand.projection();
var nativeScale = nativeProj.nominalScale();

// Define the target scale (1 km)
var targetScale = 1000;

// Get the projection at the desired scale
var projectionAt1k = popBand.projection().atScale(targetScale);

// Aggregate population to 1 km resolution
var pop1km = popBand
  .reduceResolution({
    reducer: ee.Reducer.sum().unweighted(),
    maxPixels: 1024
  })
  .reproject({
    crs: projectionAt1k
  });

// Compute total population using native settings
var populationSum = pop1km.reduceRegion({
  reducer: ee.Reducer.sum().unweighted(),
  geometry: country.geometry(),
  scale: nativeScale,
  maxPixels: 1e13
});

// Get the actual band name
var bandName = pop1km.bandNames().get(0);
var populationValue = populationSum.get(bandName);

// Print result as a clean message
print('Population sum for ' + countryname + ' (negative values masked out):', populationValue);
