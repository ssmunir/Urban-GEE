// Load datasets and setup initial variables
var population1980 = ee.Image("JRC/GHSL/P2023A/GHS_POP/1980");
var population2020 = ee.Image("JRC/GHSL/P2023A/GHS_POP/2020");
var countriesFC = ee.FeatureCollection('FAO/GAUL/2015/level0');

// Define the Mollweide projection
var mollweideProjection = ee.Projection('PROJCS["World_Mollweide",GEOGCS["GCS_WGS_1984",DATUM["WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mollweide"],PARAMETER["false_easting",0],PARAMETER["false_northing",0],PARAMETER["central_meridian",0],UNIT["Meter",1]]');

// Function to preprocess population raster and reproject to 1km scale
function preprocessPopulation(population) {
  return population.where(population.lt(0), 0)
    .reduceResolution({
      reducer: ee.Reducer.sum().unweighted(),
      maxPixels: 1024
    })
    .reproject({
      crs: population.projection().atScale(1000)
    });
}

// Load and preprocess population rasters
var pop1980 = preprocessPopulation(population1980);
var pop2020 = preprocessPopulation(population2020);

// Function to create binned images with 500-unit bins
function createBinnedImages(pop1980, pop2020) {
  var binningExpression = 
    "pop > 30000 ? 31000 : ceil(pop / 1000) * 1000";
  
  var binned1980 = pop1980
    .expression(
      binningExpression,
      {'pop': pop1980}
    ).rename('bin1980');
  
  var binned2020 = pop2020
    .expression(
      binningExpression,
      {'pop': pop2020}
    ).rename('bin2020');
    
  return {
    'binned1980': binned1980,
    'binned2020': binned2020
  };
}

// Function to process a single country
function processCountry(countryGeometry, countryName) {
  var binnedImages = createBinnedImages(pop1980, pop2020);
  var ones = ee.Image.constant(1);
  
  var analysisImage = pop2020.rename('pop2020')
    .addBands(binnedImages.binned1980)
    .addBands(binnedImages.binned2020)
    .addBands(ones.rename('count'));
  
  var stats = analysisImage.reduceRegion({
    reducer: ee.Reducer.sum().combine({
      reducer2: ee.Reducer.count(),
      sharedInputs: false
    }).group({
      groupField: 1,
      groupName: 'bin1980'
    }).group({
      groupField: 2,
      groupName: 'bin2020'
    }),
    geometry: countryGeometry,
    scale: 1000,
    maxPixels: 1e13
  });
  
  var groups = ee.List(stats.get('groups'));
  return groups.map(function(g) {
    var groupDict = ee.Dictionary(g);
    var bin2020Value = groupDict.get('bin2020');
    var subGroups = ee.List(groupDict.get('groups'));
    
    return subGroups.map(function(subGroup) {
      var subDict = ee.Dictionary(subGroup);
      return ee.Feature(null, {
        'bin1980': subDict.get('bin1980'),
        'bin2020': bin2020Value,
        'pop2020_sum': ee.Number(subDict.get('sum')).ceil(),
        'pixel_count': ee.Number(subDict.get('count')).ceil(),
        'country': countryName
      });
    });
  }).flatten();
}

// Function to process regions with simple geometries
function processRegionPopulation(countries, exportFileName) {
  var regionResults = ee.FeatureCollection([]);
  
  countries.forEach(function(countryName) {
    var countryGeometry = countriesFC
      .filter(ee.Filter.eq('ADM0_NAME', countryName))
      .geometry()
      .transform(mollweideProjection, 0.01);
    
    var countryFeatures = processCountry(countryGeometry, countryName);
    regionResults = regionResults.merge(ee.FeatureCollection(countryFeatures));
  });

  // Aggregate results for the entire region
  var aggregatedResults = regionResults.reduceColumns({
    reducer: ee.Reducer.sum().repeat(2).group({
      groupField: 0,  // bin1980
      groupName: 'bin1980'
    }).group({
      groupField: 1,  // bin2020
      groupName: 'bin2020'
    }),
    selectors: ['bin1980', 'bin2020', 'pop2020_sum', 'pixel_count']
  }).get('groups');

  var finalResults = ee.FeatureCollection(ee.List(aggregatedResults).map(function(g) {
    var groupDict = ee.Dictionary(g);
    var bin2020Value = groupDict.get('bin2020');
    var subGroups = ee.List(groupDict.get('groups'));
    
    return subGroups.map(function(subGroup) {
      var subDict = ee.Dictionary(subGroup);
      var sumList = ee.List(subDict.get('sum'));
      return ee.Feature(null, {
        'bin1980': subDict.get('bin1980'),
        'bin2020': bin2020Value,
        'pop2020_sum': sumList.get(0),
        'pixel_count': sumList.get(1)
      });
    });
  }).flatten());

  Export.table.toDrive({
    collection: finalResults,
    description: exportFileName + '_Aggregated',
     selectors: ['bin1980', 'bin2020', 'pop2020_sum', 'pixel_count'],
    fileFormat: 'CSV'
  });
}

// Function to handle complex geometries
function processDynamicRegion(countries, exportFileName) {
  var regionResults = ee.FeatureCollection([]);
  
  countries.forEach(function(countryName) {
    var countryFC = countriesFC.filter(ee.Filter.eq('ADM0_NAME', countryName));
    var countrySize = countryFC.size();

    if (countrySize.gt(1)) {
      var features = countryFC.toList(countrySize);
      
      var featureResults = features.map(function(feature) {
        feature = ee.Feature(feature);
        var featureGeometry = feature.geometry().transform(mollweideProjection, 0.01);
        return processCountry(featureGeometry, countryName);
      });

      regionResults = regionResults.merge(ee.FeatureCollection(featureResults.flatten()));
    } else {
      var countryGeometry = countryFC.geometry().transform(mollweideProjection, 0.01);
      var countryFeatures = processCountry(countryGeometry, countryName);
      regionResults = regionResults.merge(ee.FeatureCollection(countryFeatures));
    }
  });

  // Aggregate results for the entire region
  var aggregatedResults = regionResults.reduceColumns({
    reducer: ee.Reducer.sum().repeat(2).group({
      groupField: 0,  // bin1980
      groupName: 'bin1980'
    }).group({
      groupField: 1,  // bin2020
      groupName: 'bin2020'
    }),
    selectors: ['bin1980', 'bin2020', 'pop2020_sum', 'pixel_count']
  }).get('groups');

  var finalResults = ee.FeatureCollection(ee.List(aggregatedResults).map(function(g) {
    var groupDict = ee.Dictionary(g);
    var bin2020Value = groupDict.get('bin2020');
    var subGroups = ee.List(groupDict.get('groups'));
    
    return subGroups.map(function(subGroup) {
      var subDict = ee.Dictionary(subGroup);
      var sumList = ee.List(subDict.get('sum'));
      return ee.Feature(null, {
        'bin1980': subDict.get('bin1980'),
        'bin2020': bin2020Value,
        'pop2020_sum': sumList.get(0),
        'pixel_count': sumList.get(1)
      });
    });
  }).flatten());

  Export.table.toDrive({
    collection: finalResults,
    description: exportFileName + '_Aggregated',
     selectors: ['bin1980', 'bin2020', 'pop2020_sum', 'pixel_count'],
    fileFormat: 'CSV'
  });
}

// Define regions
// Sub-Saharan Africa
var SSA = ['Gambia', 'Guinea', 'Guinea-Bissau', 'Lesotho',
'Liberia', 'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Mauritius', 'Mozambique',
'Namibia', 'Niger', 'Rwanda', 'Sao Tome and Principe', 'Senegal', 'Seychelles', 
'Sierra Leone', 'Somalia', 'South Africa', 'South Sudan', 'Sudan', 'United Republic of Tanzania', 
'Togo', 'Uganda', 'Zambia', 'Zimbabwe'];

// Sub-Saharan Africa
var SSA2 = ['Angola','Nigeria', 'Ghana', 'Kenya', 'Swaziland', 'Benin',
'Botswana', 'Burkina Faso', 'Burundi', 'Cape Verde', 'Cameroon', 
'Central African Republic', 'Chad', 'Comoros', 'Congo', 
'Democratic Republic of the Congo', "Côte d'Ivoire", 'Equatorial Guinea',
'Eritrea', 'Ethiopia', 'Gabon'];

// East Asia and Pacific
var EAP =['American Samoa', 'Australia', 'Brunei Darussalam', 'Cambodia', 'China', 'Fiji',
'French Polynesia', 'Guam', 'Hong Kong', 'Indonesia', 'Japan', 'Kiribati', 
"Dem People's Rep of Korea", "Republic of Korea", "Lao People's Democratic Republic",
'Macau', 'Malaysia', 'Marshall Islands', "Micronesia (Federated States of)",
'Mongolia', 'Myanmar','Nauru', 'New Caledonia', 'New Zealand','Northern Mariana Islands',
'Palau','Papua New Guinea', 'Philippines', 'Samoa', 'Singapore', 'Solomon Islands',
'Taiwan', 'Thailand', 'Timor-Leste', 'Tonga', 'Tuvalu','Vanuatu', 'Viet Nam'
  ];
  
// Europe and Central Asia
var ECA = ['Albania', 'Andorra', 'Armenia', 'Austria', 'Azerbaijan', 'Belarus', 'Belgium'
];

// Latin America & Caribbean
var LAC = ['Antigua and Barbuda', 'Argentina', 'Aruba', 'Barbados', 'Belize', 'Bolivia', 'Brazil', 'British Virgin Islands',
'Cayman Islands', 'Chile', 'Colombia', 'Costa Rica', 'Cuba', 'Dominica', 'Dominican Republic', 'Ecuador', 'El Salvador', 
'Grenada', 'Guatemala', 'Guyana', 'Haiti', 'Honduras', 'Jamaica', 'Mexico', 'Nicaragua', 'Panama', 'Paraguay', 'Peru', 
'Puerto Rico', 'Saint Kitts and Nevis', 'Saint Vincent and the Grenadines', 'Suriname', 'Trinidad and Tobago',
'Turks and Caicos islands', 'Uruguay', 'Venezuela', 'United States Virgin Islands'
];

// Middle East & North Africa
var MENA = ['Algeria', 'Bahrain', 'Djibouti', 'Egypt', 'Iran  (Islamic Republic of)', 'Iraq', 'Israel', 'Jordan',
'Kuwait', 'Lebanon', 'Libya', 'Malta', 'Morocco', 'Oman', 'Qatar', 'Saudi Arabia', 'Syrian Arab Republic',
'Tunisia', 'United Arab Emirates', 'West Bank', 'Yemen'
  ];

//South Asia
var SA = ['Afghanistan', 'Bangladesh', 'Bhutan', 'India', 'Maldives', 'Nepal', 'Pakistan', 'Sri Lanka'
];
  
  
 
// North America 
var NA = ['Bermuda', 'Canada', 'United States of America'];

// Process each region
processDynamicRegion(EAP, 'East_Asia_and_Pacific');
processRegionPopulation(SSA2, 'Sub_Saharan_Africa2');
processRegionPopulation(SSA, 'Sub_Saharan_Africa');
processDynamicRegion(LAC, 'Latin_America_and_Caribbean');
processRegionPopulation(MENA, 'Middle_East_and_North_Africa');
processDynamicRegion(ECA, 'Europe_and_Central_Asia');
processRegionPopulation(SA, 'South_Asia');
processDynamicRegion(NA, 'North_America');