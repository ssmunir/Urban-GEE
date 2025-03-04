/************************************************************
 * Load datasets and setup initial variables
 ************************************************************/
var population1980 = ee.Image("JRC/GHSL/P2023A/GHS_POP/1980");
var population2020 = ee.Image("JRC/GHSL/P2023A/GHS_POP/2020");
var countriesFC = ee.FeatureCollection('FAO/GAUL/2015/level0');

// Define the Mollweide projection
var mollweideProjection = ee.Projection(
  'PROJCS["World_Mollweide",' +
    'GEOGCS["GCS_WGS_1984",' +
      'DATUM["WGS_1984",' +
        'SPHEROID["WGS_1984",6378137,298.257223563]],' +
      'PRIMEM["Greenwich",0],' +
      'UNIT["Degree",0.0174532925199433]],' +
    'PROJECTION["Mollweide"],' +
    'PARAMETER["false_easting",0],' +
    'PARAMETER["false_northing",0],' +
    'PARAMETER["central_meridian",0],' +
    'UNIT["Meter",1]]'
);

/************************************************************
 * Function to preprocess population raster and reproject to 1km scale
 ************************************************************/
function preprocessPopulation(popImage) {
  return popImage
    // Replace negative values with 0
    .where(popImage.lt(0), 0)
    // Aggregate to ~1km resolution
    .reduceResolution({
      reducer: ee.Reducer.sum().unweighted(),
      maxPixels: 1024
    })
    .reproject({
      crs: popImage.projection().atScale(1000)
    });
}

/************************************************************
 * Load and preprocess population rasters
 ************************************************************/
var pop1980 = preprocessPopulation(population1980);
var pop2020 = preprocessPopulation(population2020);

/************************************************************
 * Function to create binned images
 * If pixel pop > 30k, assign 31k. Otherwise round up to nearest 1000.
 ************************************************************/
function createBinnedImages(pop1980, pop2020) {
  var binExpr = "pop > 30000 ? 31000 : ceil(pop / 1000) * 1000";
  
  var binned1980 = pop1980.expression(binExpr, {
    'pop': pop1980
  }).rename('bin1980');
  
  var binned2020 = pop2020.expression(binExpr, {
    'pop': pop2020
  }).rename('bin2020');
    
  return {
    binned1980: binned1980,
    binned2020: binned2020
  };
}

/************************************************************
 * processCountry:
 *    1) Creates an Image with 4 bands (pop2020, pop1980, bin1980, bin2020).
 *    2) Uses a nested group-based reducer to sum pop2020 & pop1980
 *       grouped by bin1980 and bin2020.
 *    3) Returns a FeatureCollection (flattened), not a List<List<Feature>>.
 ************************************************************/
function processCountry(countryGeometry, countryName) {
  // Create binned rasters
  var binned = createBinnedImages(pop1980, pop2020);

  // We only keep 4 total bands (2 aggregator, 2 grouping):
  //   [pop2020, pop1980, bin1980, bin2020]
  // That way the group reducer can handle 2 sums + 2 group fields = 4 total
  var analysisImage = pop2020.rename('pop2020')
    .addBands(pop1980.rename('pop1980'))
    .addBands(binned.binned1980)
    .addBands(binned.binned2020);

  // sum().repeat(2) => sum first 2 aggregator bands => pop2020, pop1980
  // groupField: 2 => bin1980, then groupField: 3 => bin2020
  var stats = analysisImage.reduceRegion({
    reducer: ee.Reducer.sum().repeat(2)
      .group({
        groupField: 2, // 3rd band => bin1980
        groupName: 'bin1980'
      })
      .group({
        groupField: 3, // 4th band => bin2020
        groupName: 'bin2020'
      }),
    geometry: countryGeometry,
    scale: 1000,
    maxPixels: 1e13
  });

  // 'stats' is a dictionary with a nested 'groups' property
  var outerGroups = ee.List(stats.get('groups')); // each is dict with bin2020 + 'groups'

  // Convert nested structure => flattened list of Features
  var nestedFeatureList = outerGroups.map(function(outer) {
    var outerDict = ee.Dictionary(outer);
    var bin2020Val = outerDict.get('bin2020');
    var innerGroups = ee.List(outerDict.get('groups'));

    // Each 'inner' is a dictionary with bin1980 + sums
    return innerGroups.map(function(inner) {
      var innerDict = ee.Dictionary(inner);
      var sumList = ee.List(innerDict.get('sum'));
      // sumList[0] = sum of pop2020
      // sumList[1] = sum of pop1980
      return ee.Feature(null, {
        'bin1980': innerDict.get('bin1980'),
        'bin2020': bin2020Val,
        'pop2020_sum': sumList.get(0),
        'pop1980_sum': sumList.get(1),
        'country': countryName
      });
    });
  });

  // 'nestedFeatureList' is a List<List<Feature>> => flatten once
  var flatFeatures = nestedFeatureList.flatten(); // => List<Feature>
  
  // Return a FeatureCollection, so it’s not a nested list
  return ee.FeatureCollection(flatFeatures);
}

/************************************************************
 * processRegionPopulation:
 *   1) Loops over single-geometry countries
 *   2) Calls processCountry => returns FeatureCollection
 *   3) Merges those into regionResults
 *   4) Optionally aggregates region-wide sums
 ************************************************************/
function processRegionPopulation(countries, exportFileName) {
  var regionResults = ee.FeatureCollection([]);

  countries.forEach(function(countryName) {
    var countryGeom = countriesFC
      .filter(ee.Filter.eq('ADM0_NAME', countryName))
      .geometry()
      .transform(mollweideProjection, 0.01);

    // processCountry now returns a FeatureCollection
    var countryFC = processCountry(countryGeom, countryName);

    // Merge it
    regionResults = regionResults.merge(countryFC);
  });

  // regionResults is now a FeatureCollection with columns:
  //   bin1980, bin2020, pop2020_sum, pop1980_sum, country

  // If you want region-wide aggregated CSV by bin1980 and bin2020,
  // do a second reduceColumns here:
  var aggregatedResults = regionResults.reduceColumns({
    // We have 2 numeric aggregator fields => sum().repeat(2),
    // plus 2 group fields => bin1980, bin2020
    reducer: ee.Reducer.sum().repeat(2)
      .group({
        groupField: 0,  // bin1980
        groupName: 'bin1980'
      })
      .group({
        groupField: 1,  // bin2020
        groupName: 'bin2020'
      }),
    // In regionResults, we want the order:
    //   [bin1980, bin2020, pop2020_sum, pop1980_sum]
    selectors: [
      'bin1980',      // index 0 => group
      'bin2020',      // index 1 => group
      'pop2020_sum',  // index 2 => sum
      'pop1980_sum'   // index 3 => sum
    ]
  }).get('groups');

  // aggregatedResults is a nested list. Flatten it into a FeatureCollection:
  var finalResults = ee.FeatureCollection(
    ee.List(aggregatedResults).map(function(outer) {
      var outerDict = ee.Dictionary(outer);
      var bin2020Val = outerDict.get('bin2020');
      var subGroups = ee.List(outerDict.get('groups'));
      
      return subGroups.map(function(sub) {
        var subDict = ee.Dictionary(sub);
        var sumList = ee.List(subDict.get('sum'));
        return ee.Feature(null, {
          'bin1980': subDict.get('bin1980'),
          'bin2020': bin2020Val,
          'pop2020_sum': sumList.get(0),
          'pop1980_sum': sumList.get(1)
        });
      });
    }).flatten()
  );

  Export.table.toDrive({
    collection: finalResults,
    description: exportFileName + '_Aggregated',
    selectors: ['bin1980', 'bin2020', 'pop2020_sum', 'pop1980_sum'],
    fileFormat: 'CSV'
  });
}

/************************************************************
 * processDynamicRegion:
 *   1) For multi-geometry countries, we break out each geometry.
 *   2) processCountry => returns FeatureCollection
 *   3) Merge everything
 *   4) Aggregation at region level
 ************************************************************/
function processDynamicRegion(countries, exportFileName) {
  var regionResults = ee.FeatureCollection([]);

  countries.forEach(function(countryName) {
    var countryFC = countriesFC.filter(ee.Filter.eq('ADM0_NAME', countryName));
    var size = countryFC.size();
    
    if (size.gt(1)) {
      // This country has multiple geometry parts
      var partList = countryFC.toList(size);

      // Map over each geometry part
      var subResults = partList.map(function(ft) {
        var singleFeature = ee.Feature(ft);
        var geom = singleFeature.geometry().transform(mollweideProjection, 0.01);
        // processCountry => FeatureCollection
        return processCountry(geom, countryName);
      });

      // subResults is a List<FeatureCollection>
      // Flatten them all into one FeatureCollection
      var mergedParts = ee.FeatureCollection(subResults).flatten();
      regionResults = regionResults.merge(mergedParts);

    } else {
      // Single-geometry country
      var geom2 = countryFC.geometry().transform(mollweideProjection, 0.01);
      var feats2 = processCountry(geom2, countryName); // => FeatureCollection
      regionResults = regionResults.merge(feats2);
    }
  });

  // Now regionResults is a single FeatureCollection of all countries’ features

  // Next, optionally do region-wide aggregator:
  var aggregatedResults = regionResults.reduceColumns({
    reducer: ee.Reducer.sum().repeat(2)
      .group({
        groupField: 0,
        groupName: 'bin1980'
      })
      .group({
        groupField: 1,
        groupName: 'bin2020'
      }),
    selectors: [
      'bin1980',
      'bin2020',
      'pop2020_sum',
      'pop1980_sum'
    ]
  }).get('groups');

  var finalResults = ee.FeatureCollection(
    ee.List(aggregatedResults).map(function(outer) {
      var outerDict = ee.Dictionary(outer);
      var bin2020Val = outerDict.get('bin2020');
      var subGroups = ee.List(outerDict.get('groups'));
      
      return subGroups.map(function(sub) {
        var subDict = ee.Dictionary(sub);
        var sumList = ee.List(subDict.get('sum'));
        return ee.Feature(null, {
          'bin1980': subDict.get('bin1980'),
          'bin2020': bin2020Val,
          'pop2020_sum': sumList.get(0),
          'pop1980_sum': sumList.get(1)
        });
      });
    }).flatten()
  );

  Export.table.toDrive({
    collection: finalResults,
    description: exportFileName + '_Aggregated',
    selectors: ['bin1980', 'bin2020', 'pop2020_sum', 'pop1980_sum'],
    fileFormat: 'CSV'
  });
}

/************************************************************
 * Define Regions
 ************************************************************/
// Sub-Saharan Africa
var SSA = [
  'Gambia', 'Guinea', 'Guinea-Bissau', 'Lesotho',
  'Liberia', 'Madagascar', 'Malawi', 'Mali', 'Mauritania',
  'Mauritius', 'Mozambique', 'Namibia', 'Niger', 'Rwanda',
  'Sao Tome and Principe', 'Senegal', 'Seychelles', 'Sierra Leone',
  'Somalia', 'South Africa', 'South Sudan', 'Sudan',
  'United Republic of Tanzania', 'Togo', 'Uganda', 'Zambia', 'Zimbabwe'
];

// Sub-Saharan Africa (2)
var SSA2 = [
  'Angola', 'Nigeria', 'Ghana', 'Kenya', 'Swaziland', 'Benin',
  'Botswana', 'Burkina Faso', 'Burundi', 'Cape Verde', 'Cameroon',
  'Central African Republic', 'Chad', 'Comoros', 'Congo',
  'Democratic Republic of the Congo', "Côte d'Ivoire",
  'Equatorial Guinea', 'Eritrea', 'Ethiopia', 'Gabon'
];

// East Asia and Pacific
var EAP = [
  'American Samoa', 'Australia', 'Brunei Darussalam', 'Cambodia', 'China',
  'Fiji', 'French Polynesia', 'Guam', 'Hong Kong', 'Indonesia', 'Japan',
  'Kiribati', "Dem People's Rep of Korea", "Republic of Korea",
  "Lao People's Democratic Republic", 'Macau', 'Malaysia', 'Marshall Islands',
  "Micronesia (Federated States of)", 'Mongolia', 'Myanmar', 'Nauru',
  'New Caledonia', 'New Zealand', 'Northern Mariana Islands', 'Palau',
  'Papua New Guinea', 'Philippines', 'Samoa', 'Singapore', 'Solomon Islands',
  'Taiwan', 'Thailand', 'Timor-Leste', 'Tonga', 'Tuvalu', 'Vanuatu', 'Viet Nam'
];

// Europe and Central Asia
var ECA = [
  'Albania', 'Andorra', 'Armenia', 'Austria', 'Azerbaijan',
  'Belarus', 'Belgium'
  // (etc.)
];

// Latin America & Caribbean
var LAC = [
  'Antigua and Barbuda', 'Argentina', 'Aruba', 'Barbados', 'Belize',
  'Bolivia', 'Brazil', 'British Virgin Islands', 'Cayman Islands',
  'Chile', 'Colombia', 'Costa Rica', 'Cuba', 'Dominica',
  'Dominican Republic', 'Ecuador', 'El Salvador', 'Grenada', 'Guatemala',
  'Guyana', 'Haiti', 'Honduras', 'Jamaica', 'Mexico', 'Nicaragua', 'Panama',
  'Paraguay', 'Peru', 'Puerto Rico', 'Saint Kitts and Nevis',
  'Saint Vincent and the Grenadines', 'Suriname', 'Trinidad and Tobago',
  'Turks and Caicos islands', 'Uruguay', 'Venezuela',
  'United States Virgin Islands'
];

// Middle East & North Africa
var MENA = [
  'Algeria', 'Bahrain', 'Djibouti', 'Egypt', 'Iran  (Islamic Republic of)',
  'Iraq', 'Israel', 'Jordan', 'Kuwait', 'Lebanon', 'Libya', 'Malta',
  'Morocco', 'Oman', 'Qatar', 'Saudi Arabia', 'Syrian Arab Republic',
  'Tunisia', 'United Arab Emirates', 'West Bank', 'Yemen'
];

// South Asia
var SA = [
  'Afghanistan', 'Bangladesh', 'Bhutan', 'India', 'Maldives',
  'Nepal', 'Pakistan', 'Sri Lanka'
];

// North America
var NA = ['Bermuda', 'Canada', 'United States of America'];

/************************************************************
 * Execute processing 
 ************************************************************/
// For countries mostly single-geometry, use processRegionPopulation.
// For multi-geometry, use processDynamicRegion as needed.

processDynamicRegion(EAP, 'East_Asia_and_Pacific');
processRegionPopulation(SSA2, 'Sub_Saharan_Africa2');
processRegionPopulation(SSA, 'Sub_Saharan_Africa');
processDynamicRegion(LAC, 'Latin_America_and_Caribbean');
processRegionPopulation(MENA, 'Middle_East_and_North_Africa');
processDynamicRegion(ECA, 'Europe_and_Central_Asia');
processRegionPopulation(SA, 'South_Asia');
processDynamicRegion(NA, 'North_America');
