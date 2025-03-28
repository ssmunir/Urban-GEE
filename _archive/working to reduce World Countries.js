// Load countries
//var region = ee.FeatureCollection('USDOS/LSIB_SIMPLE/2017').filter(ee.Filter.eq('country_na', 'United States'));
//var countriesFC = ee.FeatureCollection('FAO/GAUL/2015/level0').filter(ee.Filter.eq('ADM0_NAME', 'United States of America');
var region = ee.FeatureCollection('UN/Geodata/BNDA_simplified/current');
//var region = ee.FeatureCollection('FAO/GAUL_SIMPLIFIED_500m/2015/level0').filter(ee.Filter.eq('ADM0_NAME', 'United States of America'));


//get population
var population = ee.Image("JRC/GHSL/P2023A/GHS_POP/2020");
var pop1km = population.where(population.lt(0), 0).reduceResolution({
    reducer: ee.Reducer.sum().unweighted(),
    maxPixels: 1024
  })
  .reproject({
    crs: population.projection().atScale(1000)
  });
  

// Make an image out of the world countries
var world_image = region
  .filter(ee.Filter.notNull(['objectid']))
  .reduceToImage({
    properties: ['objectid'],
    reducer: ee.Reducer.first()
}).reproject({
    crs: pop1km.projection()
  });


Map.setCenter(-77.27, 38.88, 10);
var viz = {min:0, max:1000, palette:['ffffff','0000FF']};
Map.addLayer(pop1km.updateMask(pop1km.neq(0)), viz, 'Pop 1km');
Map.addLayer(world_image, {}, 'countries image');
Map.addLayer(region, viz, 'countries');

/*
// Load MODIS land cover categories in 2001.
var landcover = ee.Image('MODIS/051/MCD12Q1/2001_01_01')
  // Select the IGBP classification band.
  .select('Land_Cover_Type_1');

// Load nightlights image inputs.
var nl2001 = ee.Image('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS/F152001')
  .select('stable_lights');
var nl2012 = ee.Image('NOAA/DMSP-OLS/NIGHTTIME_LIGHTS/F182012')
  .select('stable_lights');

// Compute the nightlights decadal difference, add land cover codes.
var nlDiff = nl2012.subtract(nl2001).addBands(landcover);



// Grouped a mean reducer: change of nightlights by land cover category.
var sums = pop1km.reduceRegion({
  reducer: ee.Reducer.sum().group({
    groupField: 1,
    groupName: 'code',
  }),
  geometry: region.geometry(),
  scale: 1000,
  maxPixels: 1e8
});

// Print the resultant Dictionary.
print(sums);
*/