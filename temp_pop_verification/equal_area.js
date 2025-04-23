var countries = ee.FeatureCollection('FAO/GAUL/2015/level0');
var pop2020 = ee.Image('JRC/GHSL/P2023A/GHS_POP/2020');




// Filter for Nigeria
var nigeria = countries.filter(ee.Filter.eq('ADM0_NAME', 'China')).first();

// Try multiple projections for population calculation
var projections = [
  'EPSG:3857',   // Web Mercator
  'EPSG:3410', // (Global Equal Area)
  'EPSG:3572',
  'EPSG:3576',
  'EPSG:3575'

];

// Function to compute population with different projections
function computePopulationByProjection(raster, geometry, projectionCRS) {
  var reprojectedRaster = raster
    .updateMask(raster.gt(0))
    .reproject({
      crs: projectionCRS,
      scale: 100
    });
  
  var populationSum = reprojectedRaster.reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: geometry,
    scale: 100,
    maxPixels: 1e13
  });
  
  return {
    projection: projectionCRS,
    population: populationSum
  };
}

// Compute population for each projection
var populationResults = projections.map(function(proj) {
  return computePopulationByProjection(pop2020, nigeria.geometry(), proj);
});

// Print results
print('Population by Projection', populationResults);

// Visualization of original and reproejcted rasters