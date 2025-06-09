Map.setCenter(7.7501, 12.8969, 4);

// Add Country Boundries
var countries = ee.FeatureCollection('FAO/GAUL/2015/level0');

///////////////

// Import Urbanisation Dataset
var smod1990 = ee.Image("JRC/GHSL/P2023A/GHS_SMOD/1990").select('smod_code');
var smod2000 = ee.Image("JRC/GHSL/P2023A/GHS_SMOD/2000").select('smod_code');
var smod2010 = ee.Image("JRC/GHSL/P2023A/GHS_SMOD/2010").select('smod_code');
var smod2020 = ee.Image("JRC/GHSL/P2023A/GHS_SMOD/2020").select('smod_code');
var smod2030 = ee.Image("JRC/GHSL/P2023A/GHS_SMOD/2030").select('smod_code');

/*
var smodSeries = ee.Image.cat([
  smod2000.updateMask(smod2000.gt(21)).rename('smod2000'), smod2010.updateMask(smod2010.gt(21)).rename('smod2010'),
  smod2020.updateMask(smod2020.gt(21)).rename('smod2020'), smod2030.updateMask(smod2030.gt(21)).rename('smod2030')
  ]);
*/
////////////

// Define a function to create urban binary layer
var createUrbanLayer = function(image, year) {
  var urbanLayer = image.eq(22).or(image.eq(23)).or(image.eq(30))
      .multiply(1) // Ensure it's 1 for urban areas
      .where(image.neq(22).and(image.neq(23)).and(image.neq(30)), 0); // Set non-urban areas to 0
  return urbanLayer.rename('urban_'+ year);
};

// Create urban layers for each year
var urban1990 = createUrbanLayer(smod1990, '1990');
var urban2000 = createUrbanLayer(smod2000, '2000');
var urban2010 = createUrbanLayer(smod2010, '2010');
var urban2020 = createUrbanLayer(smod2020, '2020');
var urban2030 = createUrbanLayer(smod2030, '2030');

// Combine urban layers into an multiband raster
//var urbanTimeSeries = ee.Image.cat([urban2000, urban2010, urban2020, urban2030]);


// import Population data 
var pop1990 = ee.Image('JRC/GHSL/P2023A/GHS_POP/1990');
var pop2000 = ee.Image('JRC/GHSL/P2023A/GHS_POP/2000');
var pop2010 = ee.Image('JRC/GHSL/P2023A/GHS_POP/2010');
var pop2020 = ee.Image('JRC/GHSL/P2023A/GHS_POP/2020');
var pop2030 = ee.Image('JRC/GHSL/P2023A/GHS_POP/2030');
var populationCountVis = {
  min: 0.0,
  max: 100.0,
  palette:
      ['000004', '320A5A', '781B6C', 'BB3654', 'EC6824', 'FBB41A', 'FCFFA4']
};

///////// CURRENT URBAN POPULATION

// Define function to multiply urban layer by population
var multiplyUrbanByPopulation = function(urbanLayer, populationLayer, year) {
  return urbanLayer.multiply(populationLayer).rename('population_urban_'+ year);
};

// Create population urban layers for each year (current year)
var populationUrban1990 = multiplyUrbanByPopulation(urban1990, pop1990, '1990');
var populationUrban2000 = multiplyUrbanByPopulation(urban2000, pop2000, '2000');
var populationUrban2010 = multiplyUrbanByPopulation(urban2010, pop2010, '2010');
var populationUrban2020 = multiplyUrbanByPopulation(urban2020, pop2020, '2020');
var populationUrban2030 = multiplyUrbanByPopulation(urban2030, pop2030, '2030');

// Combine all population urban layers into a single image with multiple bands
var multiBandPopulationUrban = ee.Image.cat([
  populationUrban1990,
  populationUrban2000,
  populationUrban2010,
  populationUrban2020,
  populationUrban2030
]);


//////////////////////
// Land that is urban in 2020 but was NOT urban in 2010
var newUrban2020 = urban2020
  .eq(1)
  .and(urban2010.eq(0))
  .rename('urban2020_not2010');

//////////// Urban LAG 2020/2030 -- urban today that was not urban 10/20 years ago

// Define function to get population that is urban today but was not urban n years ago
var NOTurbanlagBYpop = function(currentUrbanLayer, pastUrbanLayer, populationLayer, yearlag, year) {
  // Areas that are urban in the current year but were not urban n years ago
  var NoturbanTodayUrbanBefore = currentUrbanLayer.eq(1)        //  Urban areas today
      .and(pastUrbanLayer.eq(0));                          // non Urban areas n years ago
  // Multiply this mask with the population layer
  return NoturbanTodayUrbanBefore.multiply(populationLayer)
                            .rename(yearlag + year);
};


// Create population urban layers for each year (current year) 
var popUrban_10YearLag2010 = NOTurbanlagBYpop(urban2010, urban2000, pop2010, 'popUrban_10YearLag_', '2010');
var popUrban_10YearLag2020 = NOTurbanlagBYpop(urban2020, urban2010, pop2020, 'popUrban_10YearLag_', '2020');
var popUrban_10YearLag2030 = NOTurbanlagBYpop(urban2030, urban2020, pop2030, 'popUrban_10YearLag_', '2030');
var popUrban_20YearLag2010 = NOTurbanlagBYpop(urban2010, urban1990, pop2010, 'popUrban_20YearLag_', '2010');
var popUrban_20YearLag2020 = NOTurbanlagBYpop(urban2020, urban2000, pop2020, 'popUrban_20YearLag_', '2020');
var popUrban_20YearLag2030 = NOTurbanlagBYpop(urban2030, urban2010, pop2030, 'popUrban_20YearLag_', '2030');

// Combine all population urban layers into a single image with multiple bands
var multiBandPopUrban10YearLag = ee.Image.cat([
  popUrban_10YearLag2010,
  popUrban_10YearLag2020,
  popUrban_10YearLag2030,
  popUrban_20YearLag2010,
  popUrban_20YearLag2020,
  popUrban_20YearLag2030
]);

//////////// Urban LAG 2020/2030 -- not urban today that was urban 10/20 years ago

// Define function to get population that is non urban today but was urban 10 years ago
var urbanlagBYpop = function(currentUrbanLayer, pastUrbanLayer, populationLayer, yearlag, year) {
  // Areas that are not urban in the current year but were urban 10 years ago
  var NoturbanTodayUrbanBefore = currentUrbanLayer.eq(0)        // Non Urban areas today
      .and(pastUrbanLayer.eq(1));                          // Urban areas 10 years ago
  // Multiply this mask with the population layer
  return NoturbanTodayUrbanBefore.multiply(populationLayer)
                            .rename(yearlag + year);
};


// Create population urban layers for each year (current year) 
var NonUrbanPop_10YearLag2010 = urbanlagBYpop(urban2010, urban2000, pop2010, 'NonUrbanPop_10YearLag_', '2010');
var NonUrbanPop_10YearLag2020 = urbanlagBYpop(urban2020, urban2010, pop2020, 'NonUrbanPop_10YearLag_', '2020');
var NonUrbanPop_10YearLag2030 = urbanlagBYpop(urban2030, urban2020, pop2030, 'NonUrbanPop_10YearLag_', '2030');
var NonUrbanPop_20YearLag2010 = urbanlagBYpop(urban2010, urban1990, pop2010, 'NonUrbanPop_20YearLag_', '2010');
var NonUrbanPop_20YearLag2020 = urbanlagBYpop(urban2020, urban2000, pop2020, 'NonUrbanPop_20YearLag_', '2020');
var NonUrbanPop_20YearLag2030 = urbanlagBYpop(urban2030, urban2010, pop2030, 'NonUrbanPop_20YearLag_', '2030');


// Population change  1990\2010, 1990\2000, 2000/2020, 2010/2020,2010/2030, 2020/2030

// Calculate the change in population between 1990 and 2010
var popChange_1990_2010 = pop2010.subtract(pop1990).abs();

// Calculate the change in population between 1990 and 2000
var popChange_1990_2000 = pop2000.subtract(pop1990).abs();

// Calculate the change in population between 2000 and 2020
var popChange_2000_2020 = pop2020.subtract(pop2000).abs();

// Calculate the change in urban population between 2010 and 2020
var popChange_2010_2020 = pop2020.subtract(pop2010).abs();

// Calculate the change in urban population between 2010 and 2030
var popChange_2010_2030 = pop2030.subtract(pop2010).abs();

// Calculate the change in urban population between 2020 and 2030
var popChange_2020_2030 = pop2030.subtract(pop2020).abs();


// -------------------------------------------------------

/// Make three versions of population change by urban class:

// CLASS 1 -- cells that are only urban in y1, but not y2 times pop_changey1y2

// Define function to get cells that are only urban in y1, but not y2 times pop_changey1y2
var class1PopChange = function(currentUrbanLayer, pastUrbanLayer, popChange, yearlag, year) {
  // Areas that are not urban in y2 but were urban in y1
  var class1 =  pastUrbanLayer.eq(1)       // urban y1
      .and(currentUrbanLayer.eq(0));                          // not urban y2
  // Multiply this mask with the pop change y1 y2
  return class1.multiply(popChange)    // multiply by pop change y1 y2
                            .rename(yearlag + year);
};

// define class 1 pop change variable for 2000/2020
var c1PopChange2000_2020 = class1PopChange(urban2020, urban2000, popChange_2000_2020, 'c1UrbanPopChange_', '2000_2020') // 2000/2020
var c1PopChange2010_2020 = class1PopChange(urban2020, urban2010, popChange_2010_2020, 'c1UrbanPopChange_', '2010_2020') // 2010/2020
var c1PopChange2010_2030 = class1PopChange(urban2030, urban2010, popChange_2010_2030, 'c1UrbanPopChange_', '2010_2030') // 2010/2030
var c1PopChange2020_2030 = class1PopChange(urban2030, urban2020, popChange_2020_2030, 'c1UrbanPopChange_', '2020_2030') // 2020/2030

// -------------------------------------------------------

// CLASS 2 -- cells that are only urban in y2, but not in y1 times pop_changey1y2

// Define function to get cells that are only urban in y1, but not y2 times pop_changey1y2
var class2PopChange = function(currentUrbanLayer, pastUrbanLayer, popChange, yearlag, year) {
  // Areas that are not urban in y1 but were urban in y2
  var class2 =  pastUrbanLayer.eq(0)       // not urban y1
      .and(currentUrbanLayer.eq(1));                          //  urban y2
  // Multiply this mask with the pop change y1 y2
  return class2.multiply(popChange)    // multiply by pop change y1 y2
                            .rename(yearlag + year);
};

// define class 1 pop change variable for 2000/2020
var c2PopChange2000_2020 = class2PopChange(urban2020, urban2000, popChange_2000_2020, 'c2UrbanPopChange_', '2000_2020') // 2000/2020
var c2PopChange2010_2020 = class2PopChange(urban2020, urban2010, popChange_2010_2020, 'c2UrbanPopChange_', '2010_2020') // 2010/2020
var c2PopChange2010_2030 = class2PopChange(urban2030, urban2010, popChange_2010_2030, 'c2UrbanPopChange_', '2010_2030') // 2010/2030
var c2PopChange2020_2030 = class2PopChange(urban2030, urban2020, popChange_2020_2030, 'c2UrbanPopChange_', '2020_2030') // 2020/2030

// -------------------------------------------------------

// CLASS 3 -- cells that are urban in y2, and in y1 times pop_changey1y2

// Define function to get cells that are urban in y1 and in y2 times pop_changey1y2
var class3PopChange = function(currentUrbanLayer, pastUrbanLayer, popChange, yearlag, year) {
  // Areas that are not urban in y1 but were urban in y2
  var class3 =  pastUrbanLayer.eq(1)       //  urban y1
      .and(currentUrbanLayer.eq(1));       //  urban y2
  // Multiply this mask with the pop change y1 y2
  return class3.multiply(popChange)    // multiply by pop change y1 y2
                            .rename(yearlag + year);
};

// define class 3 pop change variable
var c3PopChange2000_2020 = class3PopChange(urban2020, urban2000, popChange_2000_2020, 'c3UrbanPopChange_', '2000_2020') // 2000/2020
var c3PopChange2010_2020 = class3PopChange(urban2020, urban2010, popChange_2010_2020, 'c3UrbanPopChange_', '2010_2020') // 2010/2020
var c3PopChange2010_2030 = class3PopChange(urban2030, urban2010, popChange_2010_2030, 'c3UrbanPopChange_', '2010_2030') // 2010/2030
var c3PopChange2020_2030 = class3PopChange(urban2030, urban2020, popChange_2020_2030, 'c3UrbanPopChange_', '2020_2030') // 2020/2030


/*
// Add population to layer
Map.addLayer(pop2000, {}, 'Population 2000');
Map.addLayer(pop2020, {}, 'Population 2020');
// Add urban data to layer
Map.addLayer(smod2000, {}, 'Degree of Urbanization 2000');
Map.addLayer(smod2020, {}, 'Degree of Urbanization 2020');
// Add the layers to the map
Map.addLayer(urbanTimeSeries.select('urban_2000'), {},  'Urban 2000');
Map.addLayer(urbanTimeSeries.select('urban_2020'), {},  'Urban 2020');
// Add the multi-band population urban layer to the map
Map.addLayer(multiBandPopulationUrban.select('population_urban_2000'), {}, 'Population in Urban Areas 2000');
Map.addLayer(multiBandPopulationUrban.select('population_urban_2020'), {}, 'Population in Urban Areas 2020');
// Add the multi-band population urban layer to the map
Map.addLayer(multiBandPopUrban10YearLag.select('popUrban_10YearLag_2000'), {}, 'Urban Population 10 year lag 2000');
Map.addLayer(multiBandPopUrban10YearLag.select('popUrban_10YearLag_2020'), {}, 'Urban Population 10 year lag 2020');
// Add the multi-band population urban layer to the map
Map.addLayer(multiBandPopUrban20YearLag.select('popUrban_20YearLag_2000'), {}, 'Urban Population 20 year lag 2000');
Map.addLayer(multiBandPopUrban20YearLag.select('popUrban_20YearLag_2020'), {}, 'Urban Population 20 year lag 2020');
*/ 

//////// ZONAL STATISTICS


// 2) FUNCTION TO AGGREGATE & EXPORT FOR ANY RASTER
function exportRasterByCountry(raster, rasterLabel, filePrefix) {
  // Mask negatives out
  var clean = raster.updateMask(raster.gte(0));
  // Select first band
  var band0 = clean.select(0);
  // Target 1 km scale & projection
  var targetScale  = 1000;
  var projAt1k     = band0.projection().atScale(targetScale);
  // Aggregate into 1 km pixels
  var agg1km = band0
    .reduceResolution({
      reducer:   ee.Reducer.sum().unweighted(),
      maxPixels: 1024
    })
    .reproject({
      crs:   projAt1k,
      scale: targetScale
    });
  // Get the actual band name
  var aggName = agg1km.bandNames().get(0);
  
  // Map over every country and compute sum
  var byCountry = countries.map(function(feat) {
    var geom = feat.geometry();
    var stats = agg1km.reduceRegion({
      reducer:   ee.Reducer.sum().unweighted(),
      geometry:  geom,
      scale:     targetScale,
      maxPixels: 1e13,
      tileScale: 4
    });
    var sum = stats.get(aggName);
    // Build Feature without computed property names
    return ee.Feature(null)
      .set('country',        feat.get('ADM0_NAME'))
      .set(rasterLabel,      sum);
  });
  
  // Export one CSV with all countries
  Export.table.toDrive({
    collection:  byCountry,
    description: rasterLabel,
    fileFormat:  'CSV',
    selectors:   ['country', rasterLabel]
  });
}

// 3) CALL THE FUNCTION FOR 2020 POPULATION
//exportRasterByCountry(pop2020, 'population_2020', 'PopByCountry');

// List of rasters with corresponding years
var rasters = [
  { image: pop2000.updateMask(pop2000.gt(0)), year: 2000, prefix: 'Population' }, // popultion
  { image: pop2010.updateMask(pop2010.gt(0)), year: 2010, prefix: 'Population' },
  { image: pop2020.updateMask(pop2020.gt(0)), year: 2020, prefix: 'Population' },
  { image: pop2030.updateMask(pop2030.gt(0)), year: 2030, prefix: 'Population' },
  
  { image: populationUrban2000.updateMask(populationUrban2000.gt(0)), year: 2000, prefix: 'UrbanPopulation' }, // urban population
  { image: populationUrban2010.updateMask(populationUrban2010.gt(0)), year: 2010, prefix: 'UrbanPopulation' },
  { image: populationUrban2020.updateMask(populationUrban2020.gt(0)), year: 2020, prefix: 'UrbanPopulation' },
  { image: populationUrban2030.updateMask(populationUrban2030.gt(0)), year: 2030, prefix: 'UrbanPopulation' },
  
  { image: popUrban_10YearLag2020.updateMask(popUrban_10YearLag2020.gt(0)), year: 2020, prefix: 'UrbanPopulation_10YearLag' }, // urban population 10 year lag
  { image: popUrban_10YearLag2030.updateMask(popUrban_10YearLag2030.gt(0)), year: 2030, prefix: 'UrbanPopulation_10YearLag' },
  
  { image: NonUrbanPop_10YearLag2020.updateMask(NonUrbanPop_10YearLag2020.gt(0)), year: 2020, prefix: 'NonUrbanPopulation_10YearLag' }, // non urban population 10 year lag
  { image: NonUrbanPop_10YearLag2030.updateMask(NonUrbanPop_10YearLag2030.gt(0)), year: 2030, prefix: 'NonUrbanPopulation_10YearLag' },
  
  { image: popUrban_20YearLag2020.updateMask(popUrban_20YearLag2020.gt(0)), year: 2020, prefix: 'UrbanPopulation_20YearLag' }, // urban population 20 year lag
  { image: popUrban_20YearLag2030.updateMask(popUrban_20YearLag2030.gt(0)), year: 2030, prefix: 'UrbanPopulation_20YearLag' },
  
  { image: NonUrbanPop_20YearLag2020.updateMask(NonUrbanPop_20YearLag2020.gt(0)), year: 2020, prefix: 'NonUrbanPopulation_20YearLag' }, // non urban population 20 year lag
  { image: NonUrbanPop_20YearLag2030.updateMask(NonUrbanPop_20YearLag2030.gt(0)), year: 2030, prefix: 'NonUrbanPopulation_20YearLag' },
  
  { image: popChange_2000_2020.updateMask(popChange_2000_2020.gt(0)), year: '2000-2020', prefix: 'PopChange_' }, // Population change
  { image: popChange_2010_2020.updateMask(popChange_2010_2020.gt(0)), year: '2010-2020', prefix: 'PopChange_' },
  { image: popChange_2010_2030.updateMask(popChange_2010_2030.gt(0)), year: '2010-2030', prefix: 'PopChange_' }, 
  { image: popChange_2020_2030.updateMask(popChange_2020_2030.gt(0)), year: '2020-2030', prefix: 'PopChange_' },
  
  { image: c1PopChange2000_2020.updateMask(c1PopChange2000_2020.gt(0)), year: '2000-2020', prefix: 'c1UrbanPopChange_' }, // Class 1 urban change
  { image: c1PopChange2010_2020.updateMask(c1PopChange2010_2020.gt(0)), year: '2010-2020', prefix: 'c1UrbanPopChange_' },
  { image: c1PopChange2010_2030.updateMask(c1PopChange2010_2030.gt(0)), year: '2010-2030', prefix: 'c1UrbanPopChange_' }, 
  { image: c1PopChange2020_2030.updateMask(c1PopChange2020_2030.gt(0)), year: '2020-2030', prefix: 'c1UrbanPopChange_' },
  
  { image: c2PopChange2000_2020.updateMask(c2PopChange2000_2020.gt(0)), year: '2000-2020', prefix: 'c2UrbanPopChange_' }, // Class 2 urban change
  { image: c2PopChange2010_2020.updateMask(c2PopChange2010_2020.gt(0)), year: '2010-2020', prefix: 'c2UrbanPopChange_' },
  { image: c2PopChange2010_2030.updateMask(c2PopChange2010_2030.gt(0)), year: '2010-2030', prefix: 'c2UrbanPopChange_' }, 
  { image: c2PopChange2020_2030.updateMask(c2PopChange2020_2030.gt(0)), year: '2020-2030', prefix: 'c2UrbanPopChange_' },
  
  { image: c3PopChange2000_2020.updateMask(c3PopChange2000_2020.gt(0)), year: '2000-2020', prefix: 'c3UrbanPopChange_' }, // Class 3 urban change
  { image: c3PopChange2010_2020.updateMask(c3PopChange2010_2020.gt(0)), year: '2010-2020', prefix: 'c3UrbanPopChange_' },
  { image: c3PopChange2010_2030.updateMask(c3PopChange2010_2030.gt(0)), year: '2010-2030', prefix: 'c3UrbanPopChange_' }, 
  { image: c3PopChange2020_2030.updateMask(c3PopChange2020_2030.gt(0)), year: '2020-2030', prefix: 'c3UrbanPopChange_' },
  
  { image: urban2020, year: '2020', prefix: 'UrbanLand' }, 
  { image: newUrban2020, year: ' ', prefix: 'urban2020not2010' }
];


// Loop through each raster and compute zonal statistics
rasters.forEach(function(r) {
  var rasterLabel = r.prefix + r.year;  // Create column name based on prefix and year
  var filePrefix = r.prefix + r.year; 
  exportRasterByCountry(r.image, rasterLabel, filePrefix);
});