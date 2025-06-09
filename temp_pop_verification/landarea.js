// Fast land‐area export: simplify geometries, then zonal‐stats

// 1) Load raw country boundaries
var countries = ee.FeatureCollection('FAO/GAUL/2015/level0');

// 2) Simplify each country to ~1 km tolerance to shrink vertex count
var simple = countries.map(function(f) {
  return f.simplify(1000)  // meters
           .copyProperties(f, ['ADM0_NAME']);
});

// 3) Build a per‐pixel area image in km²
var areaKm2 = ee.Image.pixelArea()
  .divide(1e6)             // m² → km²
  .rename('land_area_km2');

// 4) Run zonal‐stats over the simplified countries
var stats = areaKm2.reduceRegions({
  collection: simple,
  reducer: ee.Reducer.sum().setOutputs(['land_area_km2']),
  scale:     1000,
  tileScale: 4
});

// 5) Export one CSV with ADM0_NAME + land_area_km2
Export.table.toDrive({
  collection:  stats,
  description: 'AllCountries_LandArea_1km',
  fileFormat:  'CSV',
  selectors:   ['ADM0_NAME','land_area_km2']
});
