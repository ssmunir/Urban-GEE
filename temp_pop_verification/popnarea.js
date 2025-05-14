// 1) LOAD & DISSOLVE GAUL INTO PER‐COUNTRY GEOMETRIES
var rawCountries = ee.FeatureCollection('FAO/GAUL/2015/level0');
var countryNames  = rawCountries.aggregate_array('ADM0_NAME').distinct();
var countriesFC = ee.FeatureCollection(
  countryNames.map(function(name) {
    name = ee.String(name);
    var geom = rawCountries
      .filter(ee.Filter.eq('ADM0_NAME', name))
      .geometry();  // dissolves multipart
    return ee.Feature(geom, { ADM0_NAME: name });
  })
);

// 2) AGGREGATE POPULATION TO 1 km GRID CELLS
var popRaw = ee.Image('JRC/GHSL/P2023A/GHS_POP/2020');
var population1km = popRaw
  .where(popRaw.lt(0), 0)
  .reduceResolution({
    reducer:   ee.Reducer.sum().unweighted(),
    maxPixels: 1024
  })
  .reproject({
    crs:   popRaw.projection().atScale(1000),
    scale: 1000
  })
  .rename('population1km');

// 3) BUILD AN AREA BAND (m²) MASKED TO WHERE POP EXISTS
var areaBand = ee.Image.pixelArea()
  .rename('area_m2')
  .updateMask(population1km.mask());

// 4) SINGLE FUNCTION FOR ANY REGION
function processRegionPopulation(countryList, exportName) {
  var results = ee.FeatureCollection([]);
  
  countryList.forEach(function(countryName) {
    countryName = ee.String(countryName);
    var geom = countriesFC
      .filter(ee.Filter.eq('ADM0_NAME', countryName))
      .geometry();

    // sum population
    var popStats = population1km.reduceRegion({
      reducer:   ee.Reducer.sum(),
      geometry:  geom,
      crs:       'EPSG:4326',
      scale:     1000,
      maxPixels: 1e13,
      tileScale: 4
    });
    var popSum = popStats.get('population1km');
    
    // sum area in m², then convert to km²
    var areaStats = areaBand.reduceRegion({
      reducer:   ee.Reducer.sum(),
      geometry:  geom,
      crs:       'EPSG:4326',
      scale:     1000,
      maxPixels: 1e13,
      tileScale: 4
    });
    var areaM2  = areaStats.get('area_m2');
    var areaKm2 = ee.Number(areaM2).divide(1e6);
    
    // build feature
    var feat = ee.Feature(null, {
      country:    countryName,
      population: popSum,
      area_km2:   areaKm2
    });
    results = results.merge(ee.FeatureCollection([feat]));
  });
  
  // export
  Export.table.toDrive({
    collection:  results,
    description: exportName,
    fileFormat:  'CSV',
    selectors:   ['country','population','area_km2']
  });
}

// 6) DEFINE YOUR REGIONS (lists of ADM0_NAME strings)
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
var NA = ['Bermuda', 'Canada', 'United States of America'];


// 7) RUN FOR EACH REGION
// ------------------------------------------------------------
processRegionPopulation(SSA,  'SSA_Pop_Area_1km');
processRegionPopulation(EAP,  'EAP_Pop_Area_1km');
processRegionPopulation(ECA,  'ECA_Pop_Area_1km');
processRegionPopulation(LAC,  'LAC_Pop_Area_1km');
processRegionPopulation(MENA, 'MENA_Pop_Area_1km');
processRegionPopulation(SA,   'SA_Pop_Area_1km');
processRegionPopulation(NA,   'NA_Pop_Area_1km');
