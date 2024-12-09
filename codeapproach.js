function processCountryPopulationNoReduceRegion(countryName, exportFileName) {
    // Load population raster and country boundaries
    var ghsPop2020 = ee.Image("JRC/GHSL/P2023A/GHS_POP/2020");
    var countries = ee.FeatureCollection('FAO/GAUL/2015/level0');
  
    // Step 1: Create a country code raster
    var countryCodesRaster = countries.reduceToImage({
      properties: ['ADM0_CODE'],
      reducer: ee.Reducer.first()
    });
  
    // Step 2: Get the ADM0_CODE for the specified country
    var countryFeature = countries.filter(ee.Filter.eq('ADM0_NAME', countryName)).first();
    var countryCode = ee.Number(countryFeature.get('ADM0_CODE'));
  
    // Step 3: Mask the population raster by country code
    var maskedPopulation = ghsPop2020.updateMask(countryCodesRaster.eq(countryCode));
  
    // Step 4: Aggregate population to 1-km resolution
    var proj_0 = ghsPop2020.projection();
    var proj_at1km = proj_0.atScale(1000);
  
    var population1km = maskedPopulation.reduceResolution({
        reducer: ee.Reducer.sum().unweighted(),
        maxPixels: 1024
      })
      .reproject({
        crs: proj_at1km
      });
  
    // Step 5: Create a raster for binned density
    var binnedDensity = population1km.expression(
      "min(ceil(pop / 100) * 100, 30000)", {
        'pop': population1km
      }
    ).rename('binned_density');
  
    // Step 6: Compute total population and cell counts for each bin
    var bins = ee.List.sequence(0, 29900, 100).add(30000); // Include last bin (30,000+)
  
    var results = bins.map(function(binStart) {
      var binStartValue = ee.Number(binStart);
  
      // Mask for cells in the current bin
      var binMask = binnedDensity.eq(binStartValue);
  
      // Total population for the bin (sum of population values in masked cells)
      var binPopulation = population1km.updateMask(binMask)
        .reduceRegion({
          reducer: ee.Reducer.sum(),
          geometry: maskedPopulation.geometry(),
          scale: 1000,
          maxPixels: 1e9
        })
        .get('population_count'); // Extract population sum
  
      // Total grid cell count for the bin
      var binCellCount = binMask.reduceRegion({
          reducer: ee.Reducer.count(),
          geometry: maskedPopulation.geometry(),
          scale: 1000,
          maxPixels: 1e9
        })
        .get('binned_density'); // Extract cell count
  
      // Combine results into a feature
      return ee.Feature(null, {
        'Bin': binStartValue,
        'PopulationSum': ee.Number(binPopulation).or(0), // Ensure value exists
        'GridCellCount': ee.Number(binCellCount).or(0) // Ensure value exists
      });
    });
  
    // Convert results into a FeatureCollection
    var featureCollection = ee.FeatureCollection(results);
  
    // Step 7: Export the FeatureCollection to Google Drive
    Export.table.toDrive({
      collection: featureCollection,
      description: exportFileName,
      fileFormat: 'CSV',
      selectors: ['Bin', 'PopulationSum', 'GridCellCount'] // Columns to include
    });
  
    //print('Export started for:', countryName);
  }
  
  // Example: Process for Canada
  processCountryPopulationNoReduceRegion('Nigeria', 'Canada_PopulationByDensityBins');
  