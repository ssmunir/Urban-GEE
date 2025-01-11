// This script processes binned population by region and exports each region separately

// Load population data for 1980
var population1980 = ee.Image("JRC/GHSL/P2023A/GHS_POP/1980");
var countriesFC = ee.FeatureCollection('FAO/GAUL/2015/level0');

// Define the Mollweide projection
var mollweideProjection = ee.Projection('PROJCS["World_Mollweide",GEOGCS["GCS_WGS_1984",DATUM["WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.0174532925199433]],PROJECTION["Mollweide"],PARAMETER["false_easting",0],PARAMETER["false_northing",0],PARAMETER["central_meridian",0],UNIT["Meter",1]]');


// Function to preprocess population raster and reproject to 1km scale
function preprocessPopulation(population, year) {
  var population1km = population.where(population.lt(0), 0).reduceResolution({
      reducer: ee.Reducer.sum().unweighted(),
      maxPixels: 1024
    })
    .reproject({
      crs: population.projection().atScale(1000)
    });

  return population1km.rename('population_' + year);
}

// Load and preprocess 1980 population raster
var population1980 = preprocessPopulation(ee.Image("JRC/GHSL/P2023A/GHS_POP/1980"), 1980);

// Function to process regions and aggregate results for the entire region
function processRegionPopulationByYear(countries, exportFileName, year) {
  var populationYear = preprocessPopulation(ee.Image("JRC/GHSL/P2023A/GHS_POP/" + year), year);

  var regionResults = ee.FeatureCollection([]);

  countries.forEach(function (countryName) {
    var countryGeometry = countriesFC.filter(ee.Filter.eq('ADM0_NAME', countryName)).geometry();
    
    // Reproject country geometry to Mollweide projection
    var countryGeom = countryGeometry.transform(mollweideProjection, 0.01); 

    // Clip and bin the 1980 population
    var binned1980 = population1980.clip(countryGeom).expression(
      "ceil(pop / 100) * 100", {
        'pop': population1980
      }
    ).rename('binned_population');

    // Count cells within each 1980 bin
    var cellCounts = binned1980.reduceRegion({
      reducer: ee.Reducer.frequencyHistogram(),
      geometry: countryGeom,
      scale: 1000,
      tileScale: 4,
      maxPixels: 1e13
    }).get('binned_population');

    // Sum population from the other year within the 1980 bins
    var combined = populationYear.addBands(binned1980);
    var reducer = ee.Reducer.sum().group({ groupField: 1 });

    var popByBin = combined.reduceRegion({
      reducer: reducer,
      geometry: countryGeom,
      scale: 1000,
      tileScale: 4,
      maxPixels: 1e13
    });

    var groups = ee.List(popByBin.get('groups'));

    var countryFeatures = groups.map(function (group) {
      group = ee.Dictionary(group);
      return ee.Feature(null, {
        'Bin': group.get('group'),
        'PopulationSum': group.get('sum'),
        'CellCount': ee.Dictionary(cellCounts).get(group.get('group')) || 0,
        'Year': year
      });
    });

    regionResults = regionResults.merge(ee.FeatureCollection(countryFeatures));
  });

  // Aggregate results for the entire region
  var aggregatedResults = regionResults.reduceColumns({
    reducer: ee.Reducer.sum().repeat(2).group({
      groupField: 0,
      groupName: 'Bin'
    }),
    selectors: ['Bin', 'PopulationSum', 'CellCount']
  }).get('groups');

  var finalResults = ee.FeatureCollection(ee.List(aggregatedResults).map(function (group) {
    var groupDict = ee.Dictionary(group);
    return ee.Feature(null, {
      'Bin': groupDict.get('Bin'),
      'TotalPopulationSum': ee.List(groupDict.get('sum')).get(0),
      'TotalCellCount': ee.List(groupDict.get('sum')).get(1)
    });
  }));

  Export.table.toDrive({
    collection: finalResults,
    description: exportFileName + '_Aggregated_' + year,
    fileFormat: 'CSV'
  });
}

// Function to handle complex geometries (e.g., North America)
function processDynamicRegionByYear(countries, exportFileName, year) {
  var populationYear = preprocessPopulation(ee.Image("JRC/GHSL/P2023A/GHS_POP/" + year), year);
  var regionResults = ee.FeatureCollection([]);
  countries.forEach(function (countryName) {
    var countryFC = countriesFC.filter(ee.Filter.eq('ADM0_NAME', countryName));
    var countrySize = countryFC.size();

    if (countrySize.gt(1)) {
      var features = countryFC.toList(countrySize);

      var featureResults = features.map(function (feature) {
        feature = ee.Feature(feature);
        var featureGeometry = feature.geometry().transform(mollweideProjection, 0.01);

        var binned1980 = population1980.clip(featureGeometry).expression(
          "ceil(pop / 100) * 100", {
            'pop': population1980
          }
        ).rename('binned_population');
        
        // Count cells within each 1980 bin
        var cellCounts = binned1980.reduceRegion({
          reducer: ee.Reducer.frequencyHistogram(),
          geometry: featureGeometry,
          scale: 1000,
          maxPixels: 1e9
        }).get('binned_population');
      
        var combined = populationYear.addBands(binned1980);
        var reducer = ee.Reducer.sum().group({ groupField: 1 });

        var popByBin = combined.reduceRegion({
          reducer: reducer,
          geometry: featureGeometry,
          scale: 1000,
          maxPixels: 1e13
        });

        var groups = ee.List(popByBin.get('groups'));

        return groups.map(function (group) {
          group = ee.Dictionary(group);
          return ee.Feature(null, {
            'Bin': group.get('group'),
            'PopulationSum': group.get('sum'),
            'CellCount': ee.Dictionary(cellCounts).get(group.get('group')) || 0
          });
        });
      });

      regionResults = regionResults.merge(ee.FeatureCollection(featureResults.flatten()));
    } else {
      var countryGeometry = countryFC.geometry().transform(mollweideProjection, 0.01);

      var binned1980 = population1980.clip(countryGeometry).expression(
        "ceil(pop / 100) * 100", {
          'pop': population1980
        }
      ).rename('binned_population');
      
      // Count cells within each 1980 bin
      var cellCounts = binned1980.reduceRegion({
        reducer: ee.Reducer.frequencyHistogram(),
        geometry: countryGeometry,
        scale: 1000,
        maxPixels: 1e9
      }).get('binned_population');
      
      var combined = populationYear.addBands(binned1980);
      var reducer = ee.Reducer.sum().group({ groupField: 1 });

      var popByBin = combined.reduceRegion({
        reducer: reducer,
        geometry: countryGeometry,
        scale: 1000,
        maxPixels: 1e9
      });

      var groups = ee.List(popByBin.get('groups'));

      var countryFeatures = groups.map(function (group) {
        group = ee.Dictionary(group);
        return ee.Feature(null, {
          'Bin': group.get('group'),
          'PopulationSum': group.get('sum'),
          'CellCount': ee.Dictionary(cellCounts).get(group.get('group')) || 0
        });
      });

     regionResults = regionResults.merge(ee.FeatureCollection(countryFeatures));
    }
  });

  // Aggregate results for the entire region by summing PopulationSum and CellCount by Bin
  var aggregatedResults = regionResults.reduceColumns({
    reducer: ee.Reducer.sum().repeat(2).group({
      groupField: 0, // Bin column
      groupName: 'Bin'
    }),
    selectors: ['Bin', 'PopulationSum', 'CellCount']
  }).get('groups');

  // Convert aggregated results to a FeatureCollection
  var finalResults = ee.FeatureCollection(ee.List(aggregatedResults).map(function (group) {
    var groupDict = ee.Dictionary(group);
    return ee.Feature(null, {
      'Bin': groupDict.get('Bin'),
      'TotalPopulationSum': ee.List(groupDict.get('sum')).get(0),
      'TotalCellCount': ee.List(groupDict.get('sum')).get(1)
    });
  }));

  // Export the aggregated results as a single CSV
  Export.table.toDrive({
    collection: finalResults,
    description: exportFileName + '_Aggregated_' + year,
    fileFormat: 'CSV'
  });
}

// Sub-Saharan Africa
var SSA = ['Angola','Nigeria', 'Ghana', 'Kenya', 'Swaziland', 'Benin',
'Botswana', 'Burkina Faso', 'Burundi', 'Cape Verde', 'Cameroon', 
'Central African Republic', 'Chad', 'Comoros', 'Congo', 
'Democratic Republic of the Congo', "Côte d'Ivoire", 'Equatorial Guinea',
'Eritrea', 'Ethiopia', 'Gabon', 'Gambia', 'Guinea', 'Guinea-Bissau', 'Lesotho',
'Liberia', 'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Mauritius', 'Mozambique',
'Namibia', 'Niger', 'Rwanda', 'Sao Tome and Principe', 'Senegal', 'Seychelles', 
'Sierra Leone', 'Somalia', 'South Africa', 'South Sudan', 'Sudan', 'United Republic of Tanzania', 
'Togo', 'Uganda', 'Zambia', 'Zimbabwe'];

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


// Specify years to process
var yearsToProcess = [1980, 1990, 2000, 2010, 2010];

// Process each region for the specified years
yearsToProcess.forEach(function (year) {
  processDynamicRegionByYear(EAP, 'East_Asia_and_Pacific', year);
  processRegionPopulationByYear(SSA, 'Sub_Saharan_Africa', year);
  processDynamicRegionByYear(LAC, 'Latin_America_and_Caribbean', year);
  processRegionPopulationByYear(MENA, 'Middle_East_and_North_Africa', year);
  processDynamicRegionByYear(ECA, 'Europe_and_Central_Asia', year);
  processRegionPopulationByYear(SA, 'South_Asia', year);
  processDynamicRegionByYear(NA, 'North_America', year);
});