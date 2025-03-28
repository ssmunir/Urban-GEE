
https://spatialthoughts.com/2021/05/13/aggregating-population-data-gee/

// Load a region representing the United States
var region = ee.FeatureCollection('USDOS/LSIB_SIMPLE/2017');
//var region = ee.FeatureCollection('USDOS/LSIB_SIMPLE/2017').filter(ee.Filter.eq('country_na', 'United States'));
//var countriesFC = ee.FeatureCollection('FAO/GAUL/2015/level0').filter(ee.Filter.eq('ADM0_NAME', 'United States of America');
//var region = ee.FeatureCollection('UN/Geodata/BNDA_simplified/current');
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
  
//Convert US feature to image
//make a numeric code for USA
var mapping = ee.Dictionary({
  'United States': 1,
  'Mexico': 2,
  'Canada': 3,
});
var mapped = region.select(['country_na']).map(function (feature) {
    return feature.set('country_code', mapping.get(feature.get('country_na')));
  });
// Make an image out of the USA feature
var USA_image = mapped
  .filter(ee.Filter.notNull(['country_code']))
  .reduceToImage({
    properties: ['country_code'],
    reducer: ee.Reducer.first()
}).reproject({
    crs: pop1km.projection()
  });


// https://developers.google.com/earth-engine/guides/best_practices#dont_use_a_complex_collection_as_the_region_for_a_reducer


// Define a palette for the 18 distinct land cover classes.
Map.setCenter(-77.27, 38.88, 10);
var popviz = {min:0, max:1000, palette:['ffffff','0000FF']};
Map.addLayer(pop1km.updateMask(pop1km.neq(0)), popviz, 'Pop 1km');
Map.addLayer(mapped, {}, 'USA');
Map.addLayer(USA_image, {min: 1, max: 3, Palette:['0000FF', '008000','FF0000']}, 'USA image');


// Add the country codes image to pop raster
var pop1km_country = pop1km.addBands(USA_image);

//clip the image by the country collection first
var clippedTheRightWay = pop1km_country.clipToCollection(mapped);


// Grouped a mean reducer: change of nightlights by land cover category.
var sums = clippedTheRightWay.reduceRegion({
  reducer: ee.Reducer.sum().group({
    groupField: 1,
    groupName: 'country',
  }),
  geometry: ee.Geometry.Rectangle({
    coords: [-179.9, -50, 179.9, 50],  // Almost global.
    geodesic: false
  }),
  scale: 1000,
  maxPixels: 1e8
});

// Print the resultant Dictionary.
print(sums);
