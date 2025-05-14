// ============================================================
// Land Area (“pixel count”) per Country at 1 km in EPSG:4326
// Uses two functions: one for standard regions, one for multipolygon countries
// ============================================================

// 1) IMPORT & PREPARE COUNTRY GEOMETRIES
// ------------------------------------------------------------
var rawCountries = ee.FeatureCollection('FAO/GAUL/2015/level0');
var countryNames = rawCountries.aggregate_array('ADM0_NAME').distinct();
var countriesFC = ee.FeatureCollection(
  countryNames.map(function(name) {
    name = ee.String(name);
    var geom = rawCountries
      .filter(ee.Filter.eq('ADM0_NAME', name))
      .geometry();  // dissolves multipart
    return ee.Feature(geom, { ADM0_NAME: name });
  })
);

// 2) LOAD & MASK THE POPULATION RASTER (“land” = pop ≥ 0)
// ------------------------------------------------------------
var popRaw = ee.Image('JRC/GHSL/P2023A/GHS_POP/2020');
var pop2020 = popRaw.updateMask(popRaw.gte(0)).rename('pop');

// 3) REPROJECT TO 1 km GRID IN EPSG:4326 AND BUILD A BINARY “pixel” IMAGE
// ------------------------------------------------------------
var grid4326_1km = ee.Projection('EPSG:4326').atScale(1000);
var pop1km = pop2020.reproject(grid4326_1km);
var combined = pop1km
  .gt(-1)           // true for every “land” pixel
  .rename('pixel')
  .updateMask(pop1km.mask());

// 4) REGION LISTS
// ------------------------------------------------------------
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
var NA = ['Bermuda'];


// 5) LIST FOR MULTIPART‐GEOMETRY COUNTRIES
// ------------------------------------------------------------
var MULTI = ['Australia','Canada','United States of America','West Bank'];

// 6) STANDARD REGION PROCESSOR
// ------------------------------------------------------------
function processRegionLandArea(countryList, exportName) {
  var results = ee.FeatureCollection([]);
  countryList.forEach(function(name) {
    name = ee.String(name);
    var geom = countriesFC
      .filter(ee.Filter.eq('ADM0_NAME', name))
      .geometry();
    var count = combined.reduceRegion({
      reducer:   ee.Reducer.sum(),
      geometry:  geom,
      crs:       'EPSG:4326',
      scale:     1000,
      maxPixels: 1e13,
      tileScale: 4
    }).get('pixel');
    var feat = ee.Feature(null, {
      country:     name,
      pixel_count: count
    });
    results = results.merge(ee.FeatureCollection([feat]));
  });
  Export.table.toDrive({
    collection:  results,
    description: exportName,
    fileFormat:  'CSV',
    selectors:   ['country','pixel_count']
  });
}

// 7) DYNAMIC MULTIPOLYGON PROCESSOR
// ------------------------------------------------------------
function processDynamicLandArea(countryList, exportName) {
  var results = ee.FeatureCollection([]);
  countryList.forEach(function(name) {
    name = ee.String(name);
    var fc = countriesFC.filter(ee.Filter.eq('ADM0_NAME', name));
    var geom = fc.geometry();  // union of all parts
    var count = combined.reduceRegion({
      reducer:   ee.Reducer.sum(),
      geometry:  geom,
      crs:       'EPSG:4326',
      scale:     1000,
      maxPixels: 1e13,
      tileScale: 4
    }).get('pixel');
    var feat = ee.Feature(null, {
      country:     name,
      pixel_count: count
    });
    results = results.merge(ee.FeatureCollection([feat]));
  });
  Export.table.toDrive({
    collection:  results,
    description: exportName,
    fileFormat:  'CSV',
    selectors:   ['country','pixel_count']
  });
}

// 8) RUN EXPORTS
// ------------------------------------------------------------
// Standard regions
processRegionLandArea(SSA,  'SSA_LandArea_1km');
processRegionLandArea(EAP,  'EAP_LandArea_1km');
processRegionLandArea(ECA,  'ECA_LandArea_1km');
processRegionLandArea(LAC,  'LAC_LandArea_1km');
processRegionLandArea(MENA, 'MENA_LandArea_1km');
processRegionLandArea(SA,   'SA_LandArea_1km');

// Multipolygon cases
processDynamicLandArea(MULTI, 'MultiGeometry_Countries_LandArea_1km');