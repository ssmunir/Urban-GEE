// Load country boundaries and population raster
var countries = ee.FeatureCollection('FAO/GAUL/2015/level0');
var pop2020 = ee.Image('JRC/GHSL/P2023A/GHS_POP/2020');

// Mask out negative values
var popClean = pop2020.updateMask(pop2020.gte(0));

// Select country of interest
var countryname = 'Finland';
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

// Compute total population using native settings
var populationSum = popBand.reduceRegion({
  reducer: ee.Reducer.sum().unweighted(),
  geometry: country.geometry(),
  scale: nativeScale,
  maxPixels: 1e13
});

// Get the actual band name
var bandName = popBand.bandNames().get(0);
var populationValue = populationSum.get(bandName);

// Print result as a clean message
print('Population sum for ' + countryname + ' (negative values masked out):', populationValue);
