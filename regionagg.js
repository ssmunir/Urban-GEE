var population = ee.Image("JRC/GHSL/P2023A/GHS_POP/1980");
var countriesFC = ee.FeatureCollection('FAO/GAUL/2015/level0');

// Aggregate population data to 1-km grid cells
//BEFORE reducing resolution: set missing population to zero, not negative
var population1km = population.where(population.lt(0), 0).reduceResolution({
    reducer: ee.Reducer.sum().unweighted(),
    maxPixels: 1024
  })
  .reproject({
    crs: population.projection().atScale(1000)
  });
  
//Map.addLayer(population, {}, "Population");
//Map.addLayer(population1km, {}, "Population at 1km");

// Round up population values to the nearest 100 as a new raster
var binned_pop1km = population1km.expression(
  "ceil(pop / 100) * 100", {
	'pop': population1km,
  }
).rename('binned_population');

//Map.addLayer(binned_pop1km, {}, "Population at 1km round up to nearest 100");

// Combine original population data and binned raster
var combined = population1km.addBands(binned_pop1km);



// function starts------------------------------------------------------

// Unified function to process both single and multipolygon countries
function processDynamicRegion(countries, exportFileName) {
  // Initialize empty FeatureCollection to aggregate results
  var regionResults = ee.FeatureCollection([]);

  countries.forEach(function(countryName) {
    var countryFC = countriesFC.filter(ee.Filter.eq('ADM0_NAME', countryName));
    var countrySize = countryFC.size();

    // Handle each country separately to avoid projection issues
    if (countrySize.gt(1)) {
      // Handle multipolygon countries
      var features = countryFC.toList(countrySize);
      
      // Process each feature separately
      var processFeature = function(feature) {
        feature = ee.Feature(feature);
        var featureGeometry = feature.geometry();
        
        // Reproject the geometry to match the population data's projection
        //featureGeometry = featureGeometry.transform(population1km.projection(), ee.ErrorMargin(1000, 'meters'));
        
        // Clip population data to the feature geometry
        var combined_x = combined.clip(featureGeometry);
        
        // Use unbounded geometry for reduction
        //var reducerGeometry = featureGeometry.bounds();
        
        // Define reducer
        var reducer = ee.Reducer.sum().combine({
          reducer2: ee.Reducer.count(),
          sharedInputs: true
        }).group({groupField: 1});
        
        
          // Reduce to bin-level population totals with error handling
          var popByBin = combined_x.reduceRegion({
            reducer: reducer,
            geometry: featureGeometry,
            scale: 1000,
            maxPixels: 1e13
            //tileScale: 4
          });
          
          // Extract grouped data
          var groups = ee.List(popByBin.get('groups'));
          
          return ee.FeatureCollection(groups.map(function(group) {
            group = ee.Dictionary(group);
            return ee.Feature(null, {
              'Bin': group.get('group'),
              'PopulationSum': group.get('sum'),
              'GridcellCount': group.get('count'),
            });
          }));
      };
      
      // Map over all features
      var allResults = features.map(function(feature) {
        return processFeature(feature);
      });
      
      // Merge all results for multipolygon
      var mergedResults = ee.FeatureCollection(allResults).flatten();
      regionResults = regionResults.merge(mergedResults);
      
    } else {
      // Handle single geometry countries
      var countryGeometry = countriesFC.filter(ee.Filter.eq('ADM0_NAME', countryName)).geometry();
      
      var combined_x = combined.clip(countryGeometry);
      
      // Use unbounded geometry for reduction
      //var reducerGeometry = countryGeometry.bounds();
      
      // Define reducer
      var reducer = ee.Reducer.sum().combine({
        reducer2: ee.Reducer.count(),
        sharedInputs: true
      }).group({groupField: 1});
      
     
        // Reduce to bin-level population totals with error handling
        var popByBin = combined_x.reduceRegion({
          reducer: reducer,
          geometry: countryGeometry,
          scale: 1000,
          maxPixels: 1e9
          //tileScale: 4
        });
        
        // Extract grouped data
        var groups = ee.List(popByBin.get('groups'));
        
        // Create features from grouped data
        var countryFeatures = groups.map(function(group) {
          group = ee.Dictionary(group);
          return ee.Feature(null, {
            'Bin': group.get('group'),
            'PopulationSum': group.get('sum'),
            'GridcellCount': group.get('count'),
          });
        });
        
        regionResults = regionResults.merge(ee.FeatureCollection(countryFeatures));
    }
  });

  // Aggregate results by bin
  var finalResults = regionResults.reduceColumns({
    reducer: ee.Reducer.sum().repeat(2).group({
      groupField: 0,
      groupName: 'Bin',
    }),
    selectors: ['Bin', 'PopulationSum', 'GridcellCount']
  }).get('groups');

  // Convert the merged results back to a FeatureCollection
  var mergedFC = ee.FeatureCollection(ee.List(finalResults).map(function(group) {
    var groupValue = ee.Dictionary(group).get('Bin');
    var sumValue = ee.List(ee.Dictionary(group).get('sum')).get(0);
    var countValue = ee.List(ee.Dictionary(group).get('sum')).get(1);
    
    return ee.Feature(null, {
      'Bin': groupValue,
      'PopulationSum': sumValue,
      'GridcellCount': countValue
    });
  }));
  
  // Export to CSV
  Export.table.toDrive({
    collection: mergedFC,
    description: exportFileName,  // Name of your export file
    fileFormat: 'CSV'
  });
}

// Define regions

// Sub-Saharan Africa
var SSA = ['Nigeria', 'Ghana', 'Kenya', 'Swaziland', 'Benin',
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
'Macau', 'China', 'Malaysia', 'Marshall Islands', "Micronesia (Federated States of)",
'Mongolia', 'Myanmar','Nauru', 'New Caledonia', 'New Zealand','Northern Mariana Islands',
'Palau','Papua New Guinea', 'Philippines', 'Samoa', 'Singapore', 'Solomon Islands',
'Taiwan', 'Thailand', 'Timor-Leste', 'Tonga', 'Tuvalu','Vanuatu', 'Viet Nam'
  ];
  
// Europe and Central Asia
var ECA = ['Albania', 'Andorra', 'Armenia', 'Austria', 'Azerbaijan', 'Belarus', 'Belgium',
'Bosnia and Herzegovina', 'Bulgaria', 'Croatia', 'Cyprus', 'Denmark', 'Estonia', 'Faroe Islands',
'Finland', 'France', 'Georgia', 'Germany', 'Gibraltar', 'Greece', 'Greenland', 'Hungary', 'Iceland',
'Ireland', 'Isle of Man', 'Italy', 'Kazakhstan', 'Latvia', 'Liechtenstein', 'Lithuania', 'Luxembourg',
'Moldova, Republic of', 'Monaco', 'Montenegro', 'Netherlands', 'Norway', 'Poland', 'Portugal', 'Romania',
'Russian Federation', 'San Marino', 'Serbia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'Tajikistan',
'Turkmenistan', 'Turkey', 'Ukraine', 'U.K. of Great Britain and Northern Ireland', 'Uzbekistan'
];

// Latin America & Caribbean
var LAC = ['Antigua and Barbuda', 'Argentina', 'Aruba', 'Barbados', 'Belize', 'Bolivia', 'Brazil', 'Bermuda', 'British Virgin Islands',
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
var NA = ['Canada', 'United States of America'];

processDynamicRegion(EAP, 'East_Asia_and_Pacific');
processDynamicRegion(SSA, 'Sub_Saharan_Africa');
processDynamicRegion(LAC, 'Latin_America_&_Caribbean');
processDynamicRegion(MENA, 'Middle_East_&_North_Africa');
processDynamicRegion(ECA, 'Europe_and_Central_Asia');
processDynamicRegion(SA, 'South_Asia');
processDynamicRegion(NA, 'North_America');

