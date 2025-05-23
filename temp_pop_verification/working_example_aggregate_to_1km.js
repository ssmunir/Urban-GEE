//See notes: https://spatialthoughts.com/2021/05/13/aggregating-population-data-gee/

// Load country boundaries and population raster
var countries = ee.FeatureCollection('FAO/GAUL/2015/level0');
var pop2020 = ee.Image('JRC/GHSL/P2023A/GHS_POP/2020');

print('Native projection of pop raster: ', pop2020.projection().getInfo());

// Mask out negative values
var popClean = pop2020.updateMask(pop2020.gte(0));

// Check band names
print('Population image bands:', popClean.bandNames());

// Select the correct band (first band)
var popBand = popClean.select(0);
var nativeScale = popBand.projection().nominalScale();

// Get the projection at the desired scale (1 km)
var targetScale = 1000;
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


// Select country of interest
var countryname = 'Canada';
var country = countries.filter(ee.Filter.eq('ADM0_NAME', countryname)).first();

print('Working on country: ', countryname);

//NB: could try to simplify the country boundaries wiht "geometry: country.geometry().simplify(1000)"
// Compute total population using target settings
var populationSum = pop1km.reduceRegion({
  reducer: ee.Reducer.sum().unweighted(),
  geometry: country.geometry(),
  scale: targetScale,
  maxPixels: 1e13
});


// Print result as a clean message
print('Population sum for ' + countryname + ' (negative values masked out):', populationSum.get(pop1km.bandNames().get(0)));


// Map the world
Map.addLayer(countries, {color: 'grey'}, 'World Map');
// Simplify the country geometry to add to the map 
Map.addLayer(country.geometry().simplify(1000), {color: 'blue'}, 'Simplified Country Boundary');


