Map.setCenter(7.7501, 12.8969, 4);

// Add Country Boundries
var countries = ee.FeatureCollection('FAO/GAUL/2015/level0');



///////////////

// Import Urbanisation Dataset
var smod1980 = ee.Image("JRC/GHSL/P2023A/GHS_SMOD/1980").select('smod_code');
var smod1990 = ee.Image("JRC/GHSL/P2023A/GHS_SMOD/1990").select('smod_code');
var smod2000 = ee.Image("JRC/GHSL/P2023A/GHS_SMOD/2000").select('smod_code');
var smod2010 = ee.Image("JRC/GHSL/P2023A/GHS_SMOD/2010").select('smod_code');
var smod2020 = ee.Image("JRC/GHSL/P2023A/GHS_SMOD/2020").select('smod_code');
var smod2030 = ee.Image("JRC/GHSL/P2023A/GHS_SMOD/2030").select('smod_code');

var smodSeries = ee.Image.cat([
  smod1980.updateMask(smod1980.gt(21)).rename('smod1980'), smod1990.updateMask(smod1990.gt(21)).rename('smod1990'),
  smod2000.updateMask(smod2000.gt(21)).rename('smod2000'), smod2010.updateMask(smod2010.gt(21)).rename('smod2010'),
  smod2020.updateMask(smod2020.gt(21)).rename('smod2020'), smod2030.updateMask(smod2030.gt(21)).rename('smod2030')
  ]);


////////////

// Define a function to create urban binary layer
var createUrbanLayer = function(image, year) {
  var urbanLayer = image.eq(22).or(image.eq(23)).or(image.eq(30))
      .multiply(1) // Ensure it's 1 for urban areas
      .where(image.neq(22).and(image.neq(23)).and(image.neq(30)), 0); // Set non-urban areas to 0
  return urbanLayer.rename('urban_'+ year);
};

// Create urban layers for each year
var urban1980 = createUrbanLayer(smod1980, '1980');
var urban1990 = createUrbanLayer(smod1990, '1990');
var urban2000 = createUrbanLayer(smod2000, '2000');
var urban2010 = createUrbanLayer(smod2010, '2010');
var urban2020 = createUrbanLayer(smod2020, '2020');
var urban2030 = createUrbanLayer(smod2030, '2030');

// Combine urban layers into an multiband raster
var urbanTimeSeries = ee.Image.cat([urban1980, urban1990, urban2000, urban2010, urban2020, urban2030]);


// import Population data 
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

// add population estimates for 2000 to layer
//Map.addLayer(pop2000.updateMask(pop2000.gt(0)), populationCountVis, 'Population count, 2000');
//Map.addLayer(pop2010.updateMask(pop2010.gt(0)), populationCountVis, 'Population count, 2010');
//Map.addLayer(pop2020.updateMask(pop2020.gt(0)), populationCountVis, 'Population count, 2020');
//Map.addLayer(pop2030.updateMask(pop2030.gt(0)), populationCountVis, 'Population count, 2030');


///////// CURRENT URBAN POPULATION

// Define function to multiply urban layer by population
var multiplyUrbanByPopulation = function(urbanLayer, populationLayer, year) {
  return urbanLayer.multiply(populationLayer).rename('population_urban_'+ year);
};

// Create population urban layers for each year (current year)
var populationUrban2000 = multiplyUrbanByPopulation(urban2000, pop2000, '2000');
var populationUrban2010 = multiplyUrbanByPopulation(urban2010, pop2010, '2010');
var populationUrban2020 = multiplyUrbanByPopulation(urban2020, pop2020, '2020');
var populationUrban2030 = multiplyUrbanByPopulation(urban2030, pop2030, '2030');

// Combine all population urban layers into a single image with multiple bands
var multiBandPopulationUrban = ee.Image.cat([
  populationUrban2000,
  populationUrban2010,
  populationUrban2020,
  populationUrban2030
]);


//////////// 10 YEAR LAG

// Define function to multiply urban population today by urban 10 years ago
var NOTurban10lagBYpop = function(urbanLayer, populationLayer, year) {
  var noturban = urbanLayer.eq(0).multiply(1) // Ensure it's 1 for urban areas
      .where(urbanLayer.eq(1), 0); // Set non-urban areas to 0
  return noturban.multiply(populationLayer).rename('popUrban_10YearLag_'+ year);
};

// Create population urban layers for each year (current year)
var popUrban_10YearLag2000 = NOTurban10lagBYpop(urban1990, populationUrban2000, '2000');
var popUrban_10YearLag2010 = NOTurban10lagBYpop(urban2000, populationUrban2010, '2010');
var popUrban_10YearLag2020 = NOTurban10lagBYpop(urban2010, populationUrban2020, '2020');
var popUrban_10YearLag2030 = NOTurban10lagBYpop(urban2020, populationUrban2030, '2030');

// Combine all population urban layers into a single image with multiple bands
var multiBandPopUrban10YearLag = ee.Image.cat([
  popUrban_10YearLag2000,
  popUrban_10YearLag2010,
  popUrban_10YearLag2020,
  popUrban_10YearLag2030
]);


//////////// 20 YEAR LAG

// Define function to multiply urban population today by urban 10 years ago
var NOTurban20lagBYpop = function(urbanLayer, populationLayer, year) {
  var noturban = urbanLayer.eq(0).multiply(1) // Ensure it's 1 for urban areas
      .where(urbanLayer.eq(1), 0); // Set non-urban areas to 0
  return noturban.multiply(populationLayer).rename('popUrban_20YearLag_'+ year);
};

// Create population urban layers for each year (current year)
var popUrban_20YearLag2000 = NOTurban20lagBYpop(urban1980, populationUrban2000, '2000');
var popUrban_20YearLag2010 = NOTurban20lagBYpop(urban1990, populationUrban2010, '2010');
var popUrban_20YearLag2020 = NOTurban20lagBYpop(urban2000, populationUrban2020, '2020');
var popUrban_20YearLag2030 = NOTurban20lagBYpop(urban2010, populationUrban2030, '2030');

// Combine all population urban layers into a single image with multiple bands
var multiBandPopUrban20YearLag = ee.Image.cat([
  popUrban_20YearLag2000,
  popUrban_20YearLag2010,
  popUrban_20YearLag2020,
  popUrban_20YearLag2030
]);


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

//////// ZONAL STATISTICS


// Define the function to compute zonal statistics and export the results with dynamic column names
function computeZonalStatsAndExport(raster, year, rasterName, fileNamePrefix) {
 // Reproject the population raster to EPSG:4326 (WGS84) to match the countries
  var reprojectedRaster = raster.reproject({
    crs: 'EPSG:4326',
    scale: 100   // Set the resolution to 100 meters (or adjust based on your raster)
  });

  // Compute zonal statistics: sum of population for each country using the reprojected raster
  var zonalStats = reprojectedRaster.reduceRegions({
    collection: countries,               // Use the countries in their native EPSG:4326 projection
    reducer: ee.Reducer.sum(),           // Sum reducer for population
    scale: 100,                          // Keep the scale consistent with the raster
    crs: 'EPSG:4326'                     // Ensure both raster and polygons are in EPSG:4326
  });
  
 

  // Create a simplified FeatureCollection with just country name and the dynamically named sum
  var simplifiedZonalStats = zonalStats.map(function(feature) {
    var properties = {};
    properties['country'] = feature.get('ADM0_NAME');   // Get the country name
    properties[rasterName] = feature.get('sum');        // Rename the population sum column
    properties['year'] = year;                          // Add the year as a property

    return ee.Feature(null, properties);
  });

  // Export the results to Google Drive as a CSV
  Export.table.toDrive({
    collection: simplifiedZonalStats,
    description: fileNamePrefix + '_ZonalStats_' + year,  // File name with prefix and year
    fileFormat: 'CSV',
    selectors: ['country', rasterName]  // Only export these columns
  });
}


// Example call to the function for population in 2000
//computeZonalStatsAndExport(pop2000, 2000, 'Pop2000', 'Population');


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
  { image: popUrban_10YearLag2000.updateMask(popUrban_10YearLag2000.gt(0)), year: 2000, prefix: 'UrbanPopulation_10YearLag' }, // urban population 10 year lag
  { image: popUrban_10YearLag2010.updateMask(popUrban_10YearLag2010.gt(0)), year: 2010, prefix: 'UrbanPopulation_10YearLag' },
  { image: popUrban_10YearLag2020.updateMask(popUrban_10YearLag2020.gt(0)), year: 2020, prefix: 'UrbanPopulation_10YearLag' },
  { image: popUrban_10YearLag2030.updateMask(popUrban_10YearLag2030.gt(0)), year: 2030, prefix: 'UrbanPopulation_10YearLag' },
  { image: popUrban_20YearLag2000.updateMask(popUrban_20YearLag2000.gt(0)), year: 2000, prefix: 'UrbanPopulation_20YearLag' }, // urban population 20 year lag
  { image: popUrban_20YearLag2010.updateMask(popUrban_20YearLag2010.gt(0)), year: 2010, prefix: 'UrbanPopulation_20YearLag' },
  { image: popUrban_20YearLag2020.updateMask(popUrban_20YearLag2020.gt(0)), year: 2020, prefix: 'UrbanPopulation_20YearLag' },
  { image: popUrban_20YearLag2030.updateMask(popUrban_20YearLag2030.gt(0)), year: 2030, prefix: 'UrbanPopulation_20YearLag' }
];


// Loop through each raster and compute zonal statistics
rasters.forEach(function(r) {
  var rasterName = r.prefix + r.year;  // Create the dynamic column name based on prefix and year
  computeZonalStatsAndExport(r.image, r.year, rasterName, r.prefix);
});

