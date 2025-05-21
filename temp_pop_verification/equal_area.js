var countries = ee.FeatureCollection('FAO/GAUL/2015/level0');
var pop2020   = ee.Image('JRC/GHSL/P2023A/GHS_POP/2020');

// 1) Select Russia and simplify its geometry (drops tiny slivers)
var russiaFeat = countries.filter(ee.Filter.eq('ADM0_NAME', 'Sri Lanka')).first();
var russiaGeom = ee.Feature(russiaFeat)
  .geometry()
  .simplify(100);  // 1 km error tolerance

// 2) Mask to “land” (pop ≥ 0)
var masked = pop2020.updateMask(pop2020.gte(0));

// 3) Try different projections using reduceRegion’s crs+scale
var projections = [
  'EPSG:3857',
  'EPSG:3410',
  'EPSG:3572',
  'EPSG:3576',
  'EPSG:3575',
  'EPSG:3035',
  'EPSG:3573',
  'EPSG:4326'
];

function computePopulationByProjection(raster, geom, crs) {
  var stats = raster.reduceRegion({
    reducer:   ee.Reducer.sum(),
    geometry:  geom,
    crs:       crs,
    scale:     100,       // 1 km
    maxPixels: 1e13,
    tileScale: 8           // breaks the job into smaller tiles
  });
  // pull out whatever band you have (JRC is called 'population')
  var band = raster.bandNames().get(0);
  return ee.Dictionary({
    projection: crs,
    population: stats.get(band)
  });
}

var results = projections.map(function(crs) {
  return computePopulationByProjection(masked, russiaGeom, crs);
});

print('Population by projection (1 km, tileScale=8):', results);





