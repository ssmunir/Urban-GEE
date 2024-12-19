var population = ee.Image("JRC/GHSL/P2023A/GHS_POP/2020");
var countriesFC = ee.FeatureCollection('FAO/GAUL/2015/level0');

// Aggregate population data to 1-km grid cells
//BEFORE reducing resolution: set missing population to zero, not negative
var proj_0 = population.projection();
var proj_at1km = proj_0.atScale(1000);

var population1km = population.where(population.lt(0), 0).reduceResolution({
    reducer: ee.Reducer.sum().unweighted(),
    maxPixels: 1024
  })
  .reproject({
    crs: proj_at1km
  });
  
Map.addLayer(population, {}, "Population");
Map.addLayer(population1km, {}, "Population at 1km");


// function starts
function processRegionPopulation(countries, exportFileName) {
  // Initialize empty FeatureCollection to aggregate results for the region
  var regionResults = ee.FeatureCollection([]);
   // Loop through each country in the region
  countries.forEach(function (countryName) {
    // Filter the country geometry
    var countryGeometry = countriesFC.filter(ee.Filter.eq('ADM0_NAME', countryName)).geometry();

    // Clip population data to the country
    var population2 = Population1km.clip(countryGeometry);

    // Create a new raster by rounding up population values to the nearest 100
    var binnedPopulation = population2.expression(
      "ceil(pop / 100) * 100", {
        'pop': population2,
      }
    ).rename('binned_population');

    // Combine original population data and binned raster
    var combined = population2.addBands(binnedPopulation)

    // Reduce to bin-level population totals
    var popByBin = combined.reduceRegion({
      reducer: ee.Reducer.sum().group({
        groupField: 1,
      }),
      geometry: countryGeometry,
      scale: 1000,
      maxPixels: 1e9,
    });

    // Extract grouped data
    var groups = ee.List(ee.Dictionary(popByBin).get('groups'));

    // Create a FeatureCollection from grouped data for the country
    var countryFeatures = groups.map(function (group) {
      group = ee.Dictionary(group);
      return ee.Feature(null, {
        'Bin': group.get('group'), // Bin ID
        'PopulationSum': group.get('sum'), // Population sum for the bin
      });
    });
  // Append country results to the region's FeatureCollection
  regionResults = regionResults.merge(ee.FeatureCollection(countryFeatures));
});
  var merged = regionResults.reduceColumns({
    reducer: ee.Reducer.sum().group({
      groupField: 0,  // Index of the column to group by
      groupName: 'Bin',
    }),
    selectors: ['Bin', 'PopulationSum']  
  }).get('groups');

  // Convert the merged results back to a FeatureCollection
  var mergedFC = ee.FeatureCollection(ee.List(merged).map(function(group) {
    var groupValue = ee.Dictionary(group).get('Bin');
    var sumValue = ee.Dictionary(group).get('sum');
    
    return ee.Feature(null, {
      'Bin': groupValue,
      'PopulationSum': sumValue
    });
  }));

  // Export to CSV
  Export.table.toDrive({
    collection: mergedFC,
    description: exportFileName,  // Name of your export file
    fileFormat: 'CSV'
  });
}
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
var NA = ['Canada', 'United States of America']
  
processRegionPopulation(EAP, 'East_Asia_and_Pacific');


    
    
