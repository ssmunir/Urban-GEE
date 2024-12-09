function processCountryPopulationWithMultipleGeometries(countryName, exportFileName) {
    var ghsPop2020 = ee.Image("JRC/GHSL/P2023A/GHS_POP/2020");
    var countries = ee.FeatureCollection('FAO/GAUL/2015/level0');
  
    // Get the country as a FeatureCollection
    var countryFeatures = countries.filter(ee.Filter.eq('ADM0_NAME', countryName));
  
    // Check if the country has multiple geometries
    var geometryList = countryFeatures.toList(countryFeatures.size());
  
    // Function to process each geometry and collect population statistics
    var results = geometryList.map(function(feature) {
      var geom = ee.Feature(feature).geometry();
  
      // Clip the population raster by the current geometry
      var population = ghsPop2020.clip(geom);
  
      // Aggregate population data to 1-km resolution
      var proj_0 = population.projection();
      var proj_at1km = proj_0.atScale(1000);
  
      var population1km = population.reduceResolution({
          reducer: ee.Reducer.sum().unweighted(),
          maxPixels: 1024
        })
        .reproject({
          crs: proj_at1km
        });
  
      // Create a new raster by rounding up population values to the nearest 100
      var roundedRaster = population1km.expression(
        "ceil(pop / 100) * 100", {
          'pop': population1km
        }
      ).rename('rounded_population');
  
      // Combine population and binned data
      var combined = population1km.addBands(roundedRaster);
  
      // Compute population by bins
      var popByBin = combined.reduceRegion({
        reducer: ee.Reducer.sum().group({
          groupField: 1
        }),
        geometry: geom,
        scale: 1000,
        maxPixels: 1e9
      });
  
      return popByBin;
    });
  
    // Merge and sum results across all geometries
    var mergedResults = ee.List(results).iterate(function(result, accumulated) {
      var current = ee.Dictionary(result);
      var accumulatedDict = ee.Dictionary(accumulated);
  
      var groups = ee.List(current.get('groups'));
      var updatedGroups = groups.map(function(group) {
        var groupDict = ee.Dictionary(group);
        var bin = groupDict.get('group');
        var population = groupDict.get('sum');
  
        var updatedSum = ee.Number(accumulatedDict.get(bin, 0)).add(population);
        return ee.Dictionary({
          group: bin,
          sum: updatedSum
        });
      });
  
      return ee.Dictionary(updatedGroups.flatten());
    }, ee.Dictionary({}));
  
    // Create a FeatureCollection from the merged results
    var mergedFeatures = ee.List(mergedResults).map(function(item) {
      var dict = ee.Dictionary(item);
      return ee.Feature(null, {
        'Bin': dict.get('group'),
        'PopulationSum': dict.get('sum')
      });
    });
  
    var featureCollection = ee.FeatureCollection(mergedFeatures);
  
    // Export to Drive
    Export.table.toDrive({
      collection: featureCollection,
      description: exportFileName,
      fileFormat: 'CSV',
      selectors: ['Bin', 'PopulationSum']
    });
  
    print('Export started for:', countryName);
  }
  
  // Example usage
  processCountryPopulationWithMultipleGeometries('Canada', 'Canada_PopulationByBin');
  