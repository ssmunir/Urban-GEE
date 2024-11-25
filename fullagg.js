function processCountryPopulation(countryName, exportFileName, customGeometry) {
  var ghsPop2020 = ee.Image("JRC/GHSL/P2023A/GHS_POP/2020");

  // Use the custom geometry if provided; otherwise, fetch the country's geometry
  var region = customGeometry || ee.FeatureCollection('FAO/GAUL/2015/level0')
    .filter(ee.Filter.eq('ADM0_NAME', countryName))
    .geometry();

  // Clip the population data to the region
  var population = ghsPop2020.clip(region);

  // Aggregate population data to 1-km grid cells
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

  // Combine original population data and rounded raster
  var combined = population1km.addBands(roundedRaster);

  // Compute population by bins
  var popByBin = combined.reduceRegion({
    reducer: ee.Reducer.sum().group({
      groupField: 1
    }),
    geometry: region,
    scale: 1000,
    maxPixels: 1e9
  });

  // Extract grouped data
  var groups = ee.List(ee.Dictionary(popByBin).get('groups'));

  // Create a FeatureCollection from the grouped data
  var features = groups.map(function(group) {
    group = ee.Dictionary(group); // Cast as dictionary
    return ee.Feature(null, {
      'Bin': group.get('group'), // Bin ID
      'PopulationSum': group.get('sum') // Population sum for the bin
    });
  });

  var featureCollection = ee.FeatureCollection(features);

  // Export the FeatureCollection to Drive
  Export.table.toDrive({
    collection: featureCollection,
    description: exportFileName,
    fileFormat: 'CSV',
    selectors: ['Bin', 'PopulationSum'] // Columns to include
  });

  //print('Export started for:', countryName);
}


//processCountryPopulation('Nigeria', 'Nigeria_PopulationByBin');




// List of regions to process
// Sub saharan Africa
/*
var SSA = ['Nigeria', 'Ghana', 'Kenya', 'Swaziland', 'Benin',
'Botswana', 'Burkina Faso', 'Burundi', 'Cape Verde', 'Cameroon', 
'Central African Republic', 'Chad', 'Comoros', 'Congo', 
'Democratic Republic of the Congo', "Côte d'Ivoire", 'Equatorial Guinea',
'Eritrea', 'Ethiopia', 'Gabon', 'Gambia', 'Guinea', 'Guinea-Bissau', 'Lesotho',
'Liberia', 'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Mauritius', 'Mozambique',
'Namibia', 'Niger', 'Rwanda', 'Sao Tome and Principe', 'Senegal', 'Seychelles', 
'Sierra Leone', 'Somalia', 'South Africa', 'South Sudan', 'Sudan', 'United Republic of Tanzania', 
'Togo', 'Uganda', 'Zambia', 'Zimbabwe'];




SSA.forEach(function(country) {
  var fileName = country + '_PopulationByBin_SSA'; // Dynamically generate file name
  processCountryPopulation(country, fileName);
});
*/

// North America

var countries = ee.FeatureCollection('FAO/GAUL/2015/level0');

// Filter for Canada
var canada = countries.filter(ee.Filter.eq('ADM0_NAME', 'Canada'));
// Merge all geometries into one
var mergedCanada = canada.geometry().dissolve(); // Combines all geometries into a single one
// Print the merged geometry for inspection
//print('Merged Canada Geometry:', mergedCanada);

// Use this merged geometry to process population data
processCountryPopulation('Canada', 'Canada_PopulationByBin', mergedCanada);
processCountryPopulation('United States of America', 'USA_PopulationByBin');



/*
// East Asia and Pacific

var EAP =['American Samoa', 'Australia', 'Brunei Darussalam', 'Cambodia', 'China', 'Fiji',
'French Polynesia', 'Guam', 'Hong Kong', 'Indonesia', 'Japan', 'Kiribati', 
"Dem People's Rep of Korea", "Republic of Korea", "Lao People's Democratic Republic",
'Macau', 'China', 'Malaysia', 'Marshall Islands', "Micronesia (Federated States of)",
'Mongolia', 'Myanmar','Nauru', 'New Caledonia', 'New Zealand','Northern Mariana Islands',
'Palau','Papua New Guinea', 'Philippines', 'Samoa', 'Singapore', 'Solomon Islands',
'Taiwan', 'Thailand', 'Timor-Leste', 'Tonga', 'Tuvalu','Vanuatu', 'Viet Nam'
  ];
  
  
EAP.forEach(function(country) {
  var fileName = country + '_PopulationByBin_EAP'; // Dynamically generate file name
  processCountryPopulation(country, fileName);
});
  
// Europe and Central Asia

var ECA = ['Albania', 'Andorra', 'Armenia', 'Austria', 'Azerbaijan', 'Belarus', 'Belgium',
'Bosnia and Herzegovina', 'Bulgaria', 'Croatia', 'Cyprus', 'Denmark', 'Estonia', 'Faroe Islands',
'Finland', 'France', 'Georgia', 'Germany', 'Gibraltar', 'Greece', 'Greenland', 'Hungary', 'Iceland',
'Ireland', 'Isle of Man', 'Italy', 'Kazakhstan', 'Latvia', 'Liechtenstein', 'Lithuania', 'Luxembourg',
'Moldova, Republic of', 'Monaco', 'Montenegro', 'Netherlands', 'Norway', 'Poland', 'Portugal', 'Romania',
'Russian Federation', 'San Marino', 'Serbia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'Tajikistan',
'Turkmenistan', 'Turkey', 'Ukraine', 'U.K. of Great Britain and Northern Ireland', 'Uzbekistan'
];


ECA.forEach(function(country) {
  var fileName = country + '_PopulationByBin_ECA'; // Dynamically generate file name
  processCountryPopulation(country, fileName);
});

// Latin America & Caribbean

var LAC = ['Antigua and Barbuda', 'Argentina', 'Aruba', 'Barbados', 'Belize', 'Bolivia', 'Brazil', 'British Virgin Islands',
'Cayman Islands', 'Chile', 'Colombia', 'Costa Rica', 'Cuba', 'Dominica', 'Dominican Republic', 'Ecuador', 'El Salvador', 
'Grenada', 'Guatemala', 'Guyana', 'Haiti', 'Honduras', 'Jamaica', 'Mexico', 'Nicaragua', 'Panama', 'Paraguay', 'Peru', 
'Puerto Rico', 'Saint Kitts and Nevis', 'Saint Vincent and the Grenadines', 'Suriname', 'Trinidad and Tobago',
'Turks and Caicos islands', 'Uruguay', 'Venezuela', 'United States Virgin Islands'
];

LAC.forEach(function(country) {
  var fileName = country + '_PopulationByBin_LAC'; // Dynamically generate file name
  processCountryPopulation(country, fileName);
});

// Middle East & North Africa

var MENA = ['Algeria', 'Bahrain', 'Djibouti', 'Egypt', 'Iran  (Islamic Republic of)', 'Iraq', 'Israel', 'Jordan',
'Kuwait', 'Lebanon', 'Libya', 'Malta', 'Morocco', 'Oman', 'Qatar', 'Saudi Arabia', 'Syrian Arab Republic',
'Tunisia', 'United Arab Emirates', 'West Bank', 'Yemen'
  ];
  
  
MENA.forEach(function(country) {
  var fileName = country + '_PopulationByBin_MENA'; // Dynamically generate file name
  processCountryPopulation(country, fileName);
});



//South Asia

var SA = ['Afghanistan', 'Bangladesh', 'Bhutan', 'India', 'Maldives', 'Nepal', 'Pakistan', 'Sri Lanka'
];
  
SA.forEach(function(country) {
  var fileName = country + '_PopulationByBin_SA'; // Dynamically generate file name
  processCountryPopulation(country, fileName);
});
  

*/

