Map.setCenter(7.7501, 12.8969, 4);

// Add Country Boundaries
var countries = ee.FeatureCollection('FAO/GAUL/2015/level0');

// Print projection information for better understanding
print('Countries collection size:', countries.size());
print('Countries projection info:', countries.first().geometry().projection());

///////////////
// Import Urbanisation Dataset
var smod2000 = ee.Image("JRC/GHSL/P2023A/GHS_SMOD/2000").select('smod_code');
var smod2010 = ee.Image("JRC/GHSL/P2023A/GHS_SMOD/2010").select('smod_code');
var smod2020 = ee.Image("JRC/GHSL/P2023A/GHS_SMOD/2020").select('smod_code');
var smod2030 = ee.Image("JRC/GHSL/P2023A/GHS_SMOD/2030").select('smod_code');

// Print native projection and scale
print('SMOD 2020 projection:', smod2020.projection().getInfo());
print('SMOD 2020 native scale:', smod2020.projection().nominalScale());

////////////
// Define a function to create urban binary layer
var createUrbanLayer = function(image, year) {
  var urbanLayer = image.eq(22).or(image.eq(23)).or(image.eq(30))
      .multiply(1) // Ensure it's 1 for urban areas
      .where(image.neq(22).and(image.neq(23)).and(image.neq(30)), 0); // Set non-urban areas to 0
  return urbanLayer.rename('urban_'+ year);
};

// Create urban layers for each year
var urban2000 = createUrbanLayer(smod2000, '2000');
var urban2010 = createUrbanLayer(smod2010, '2010');
var urban2020 = createUrbanLayer(smod2020, '2020');
var urban2030 = createUrbanLayer(smod2030, '2030');

// Import Population data 
var pop2000 = ee.Image('JRC/GHSL/P2023A/GHS_POP/2000');
var pop2010 = ee.Image('JRC/GHSL/P2023A/GHS_POP/2010');
var pop2020 = ee.Image('JRC/GHSL/P2023A/GHS_POP/2020');
var pop2030 = ee.Image('JRC/GHSL/P2023A/GHS_POP/2030');

// Print population data information
print('Population 2020 projection:', pop2020.projection().getInfo());
print('Population 2020 native scale:', pop2020.projection().nominalScale());
print('Population 2020 bands:', pop2020.bandNames());

// Clean population data (mask out negative values)
var pop2000Clean = pop2000.updateMask(pop2000.gte(0));
var pop2010Clean = pop2010.updateMask(pop2010.gte(0));
var pop2020Clean = pop2020.updateMask(pop2020.gte(0));
var pop2030Clean = pop2030.updateMask(pop2030.gte(0));

// Define visualization params
var populationCountVis = {
  min: 0.0,
  max: 100.0,
  palette: ['000004', '320A5A', '781B6C', 'BB3654', 'EC6824', 'FBB41A', 'FCFFA4']
};

///////// CURRENT URBAN POPULATION
// Define function to multiply urban layer by population
var multiplyUrbanByPopulation = function(urbanLayer, populationLayer, year) {
  return urbanLayer.multiply(populationLayer).rename('population_urban_'+ year);
};

// Create population urban layers for each year (current year)
var populationUrban2000 = multiplyUrbanByPopulation(urban2000, pop2000Clean, '2000');
var populationUrban2010 = multiplyUrbanByPopulation(urban2010, pop2010Clean, '2010');
var populationUrban2020 = multiplyUrbanByPopulation(urban2020, pop2020Clean, '2020');
var populationUrban2030 = multiplyUrbanByPopulation(urban2030, pop2030Clean, '2030');

// Combine all population urban layers into a single image with multiple bands
var multiBandPopulationUrban = ee.Image.cat([
  populationUrban2000,
  populationUrban2010,
  populationUrban2020,
  populationUrban2030
]);

//////////// Urban LAG 2020/2030 -- urban today that was not urban 10/20 years ago
// Define function to get population that is urban today but was not urban n years ago
var NOTurbanlagBYpop = function(currentUrbanLayer, pastUrbanLayer, populationLayer, yearlag, year) {
  // Areas that are urban in the current year but were not urban n years ago
  var NoturbanTodayUrbanBefore = currentUrbanLayer.eq(1)        //  Urban areas today
      .and(pastUrbanLayer.eq(0));                          // non Urban areas n years ago
  // Multiply this mask with the population layer
  return NoturbanTodayUrbanBefore.multiply(populationLayer)
                            .rename(yearlag + year);
};

// Create population urban layers for each year (current year) 
var popUrban_10YearLag2020 = NOTurbanlagBYpop(urban2020, urban2010, pop2020Clean, 'popUrban_10YearLag_', '2020');
var popUrban_10YearLag2030 = NOTurbanlagBYpop(urban2030, urban2020, pop2030Clean, 'popUrban_10YearLag_', '2030');
var popUrban_20YearLag2020 = NOTurbanlagBYpop(urban2020, urban2000, pop2020Clean, 'popUrban_20YearLag_', '2020');
var popUrban_20YearLag2030 = NOTurbanlagBYpop(urban2030, urban2010, pop2030Clean, 'popUrban_20YearLag_', '2030');

// Combine all population urban layers into a single image with multiple bands
var multiBandPopUrban10YearLag = ee.Image.cat([
  popUrban_10YearLag2020,
  popUrban_10YearLag2030,
  popUrban_20YearLag2020,
  popUrban_20YearLag2030
]);

//////////// Urban LAG 2020/2030 -- not urban today that was urban 10/20 years ago
// Define function to get population that is non urban today but was urban 10 years ago
var urbanlagBYpop = function(currentUrbanLayer, pastUrbanLayer, populationLayer, yearlag, year) {
  // Areas that are not urban in the current year but were urban 10 years ago
  var NoturbanTodayUrbanBefore = currentUrbanLayer.eq(0)        // Non Urban areas today
      .and(pastUrbanLayer.eq(1));                          // Urban areas 10 years ago
  // Multiply this mask with the population layer
  return NoturbanTodayUrbanBefore.multiply(populationLayer)
                            .rename(yearlag + year);
};

// Create population urban layers for each year (current year) 
var NonUrbanPop_10YearLag2020 = urbanlagBYpop(urban2020, urban2010, pop2020Clean, 'NonUrbanPop_10YearLag_', '2020');
var NonUrbanPop_10YearLag2030 = urbanlagBYpop(urban2030, urban2020, pop2030Clean, 'NonUrbanPop_10YearLag_', '2030');
var NonUrbanPop_20YearLag2020 = urbanlagBYpop(urban2020, urban2000, pop2020Clean, 'NonUrbanPop_20YearLag_', '2020');
var NonUrbanPop_20YearLag2030 = urbanlagBYpop(urban2030, urban2010, pop2030Clean, 'NonUrbanPop_20YearLag_', '2030');

// Population change calculations
// Calculate the change in population between 2000 and 2020
var popChange_2000_2020 = pop2020Clean.subtract(pop2000Clean).abs();
var popChange_2010_2020 = pop2020Clean.subtract(pop2010Clean).abs();
var popChange_2010_2030 = pop2030Clean.subtract(pop2010Clean).abs();
var popChange_2020_2030 = pop2030Clean.subtract(pop2020Clean).abs();

/// Make three versions of population change by urban class:
// CLASS 1 -- cells that are only urban in y1, but not y2 times pop_changey1y2
var class1PopChange = function(currentUrbanLayer, pastUrbanLayer, popChange, yearlag, year) {
  // Areas that are not urban in y2 but were urban in y1
  var class1 = pastUrbanLayer.eq(1)       // urban y1
      .and(currentUrbanLayer.eq(0));      // not urban y2
  // Multiply this mask with the pop change y1 y2
  return class1.multiply(popChange)       // multiply by pop change y1 y2
               .rename(yearlag + year);
};

// Define class 1 pop change variables
var c1PopChange2000_2020 = class1PopChange(urban2020, urban2000, popChange_2000_2020, 'c1UrbanPopChange_', '2000_2020');
var c1PopChange2010_2020 = class1PopChange(urban2020, urban2010, popChange_2010_2020, 'c1UrbanPopChange_', '2010_2020');
var c1PopChange2010_2030 = class1PopChange(urban2030, urban2010, popChange_2010_2030, 'c1UrbanPopChange_', '2010_2030');
var c1PopChange2020_2030 = class1PopChange(urban2030, urban2020, popChange_2020_2030, 'c1UrbanPopChange_', '2020_2030');

// CLASS 2 -- cells that are only urban in y2, but not in y1 times pop_changey1y2
var class2PopChange = function(currentUrbanLayer, pastUrbanLayer, popChange, yearlag, year) {
  // Areas that are not urban in y1 but were urban in y2
  var class2 = pastUrbanLayer.eq(0)       // not urban y1
      .and(currentUrbanLayer.eq(1));      // urban y2
  // Multiply this mask with the pop change y1 y2
  return class2.multiply(popChange)       // multiply by pop change y1 y2
               .rename(yearlag + year);
};

// Define class 2 pop change variables
var c2PopChange2000_2020 = class2PopChange(urban2020, urban2000, popChange_2000_2020, 'c2UrbanPopChange_', '2000_2020');
var c2PopChange2010_2020 = class2PopChange(urban2020, urban2010, popChange_2010_2020, 'c2UrbanPopChange_', '2010_2020');
var c2PopChange2010_2030 = class2PopChange(urban2030, urban2010, popChange_2010_2030, 'c2UrbanPopChange_', '2010_2030');
var c2PopChange2020_2030 = class2PopChange(urban2030, urban2020, popChange_2020_2030, 'c2UrbanPopChange_', '2020_2030');

// CLASS 3 -- cells that are urban in y2, and in y1 times pop_changey1y2
var class3PopChange = function(currentUrbanLayer, pastUrbanLayer, popChange, yearlag, year) {
  // Areas that are urban in y1 and urban in y2
  var class3 = pastUrbanLayer.eq(1)       // urban y1
      .and(currentUrbanLayer.eq(1));      // urban y2
  // Multiply this mask with the pop change y1 y2
  return class3.multiply(popChange)       // multiply by pop change y1 y2
               .rename(yearlag + year);
};

// Define class 3 pop change variables
var c3PopChange2000_2020 = class3PopChange(urban2020, urban2000, popChange_2000_2020, 'c3UrbanPopChange_', '2000_2020');
var c3PopChange2010_2020 = class3PopChange(urban2020, urban2010, popChange_2010_2020, 'c3UrbanPopChange_', '2010_2020');
var c3PopChange2010_2030 = class3PopChange(urban2030, urban2010, popChange_2010_2030, 'c3UrbanPopChange_', '2010_2030');
var c3PopChange2020_2030 = class3PopChange(urban2030, urban2020, popChange_2020_2030, 'c3UrbanPopChange_', '2020_2030');

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

//////// ZONAL STATISTICS - IMPROVED VERSION

// Function to process a single country and calculate stats for a raster
function calculateCountryStats(countryName, raster, rasterName) {
  try {
    // Filter to get the country
    var country = countries.filter(ee.Filter.eq('ADM0_NAME', countryName)).first();
    
    // Skip if country not found
    if (country === null) {
      print('Country not found:', countryName);
      return null;
    }
    
    // Get the native projection and scale
    var nativeProj = raster.projection();
    var nativeScale = nativeProj.nominalScale();
    
    // Calculate statistics using native projection and scale
    var stats = raster.reduceRegion({
      reducer: ee.Reducer.sum().unweighted(),
      geometry: country.geometry(),
      scale: nativeScale,
      maxPixels: 1e13
    });
    
    // Get the actual band name
    var bandName = raster.bandNames().get(0);
    var statValue = stats.get(bandName);
    
    // Create a feature with the results
    var properties = {
      'country': countryName,
      'region': getRegionForCountry(countryName),
      'statistic': statValue
    };
    
    return ee.Feature(null, properties);
  } catch (error) {
    print('Error processing ' + countryName + ':', error);
    return null;
  }
}

// Function to identify which region a country belongs to
function getRegionForCountry(countryName) {
  if (SSA.indexOf(countryName) >= 0) return 'Sub-Saharan Africa';
  if (EAP.indexOf(countryName) >= 0) return 'East Asia and Pacific';
  if (ECA.indexOf(countryName) >= 0) return 'Europe and Central Asia';
  if (LAC.indexOf(countryName) >= 0) return 'Latin America and Caribbean';
  if (MENA.indexOf(countryName) >= 0) return 'Middle East and North Africa';
  if (SA.indexOf(countryName) >= 0) return 'South Asia';
  if (NA.indexOf(countryName) >= 0) return 'North America';
  return 'Other';
}

// Get all country names
var allCountryNames = countries.aggregate_array('ADM0_NAME');

// Process countries by region and export results
function processRegionAndExport(region, regionName, raster, year, rasterName, prefix) {
  print('Processing region:', regionName, 'for year:', year);
  
  // Filter countries in the region
  var regionFilter = ee.Filter.inList('ADM0_NAME', region);
  var regionalCountries = countries.filter(regionFilter);
  
  // Function to calculate stats for a single country
  var calculateStatsForFeature = function(feature) {
    var countryName = feature.get('ADM0_NAME');
    
    // Calculate stats using native projection
    var stats = raster.reduceRegion({
      reducer: ee.Reducer.sum().unweighted(),
      geometry: feature.geometry(),
      scale: raster.projection().nominalScale(),
      maxPixels: 1e13
    });
    
    // Get the band name
    var bandName = raster.bandNames().get(0);
    
    // Create a new feature with results
    var properties = {
      'country': countryName,
      'region': regionName
    };
    properties[rasterName] = stats.get(bandName);
    
    return ee.Feature(null, properties);
  };
  
  // Process all countries in the region
  var regionalStats = regionalCountries.map(calculateStatsForFeature);
  
  // Export the results
  Export.table.toDrive({
    collection: regionalStats,
    description: prefix + '_' + regionName.replace(/\s+/g, '_') + '_' + year,
    fileFormat: 'CSV',
    selectors: ['country', 'region', rasterName]
  });
  
  return regionalStats;
}

// List of all regions for processing
var allRegions = [
  {list: SSA, name: 'Sub-Saharan Africa'},
  {list: EAP, name: 'East Asia and Pacific'},
  {list: ECA, name: 'Europe and Central Asia'},
  {list: LAC, name: 'Latin America and Caribbean'},
  {list: MENA, name: 'Middle East and North Africa'},
  {list: SA, name: 'South Asia'},
  {list: NA, name: 'North America'}
];

// List of rasters with corresponding years
var rasters = [
  { image: pop2000Clean, year: 2000, prefix: 'Population' },
  { image: pop2010Clean, year: 2010, prefix: 'Population' },
  { image: pop2020Clean, year: 2020, prefix: 'Population' },
  { image: pop2030Clean, year: 2030, prefix: 'Population' },
  
  { image: populationUrban2000, year: 2000, prefix: 'UrbanPopulation' },
  { image: populationUrban2010, year: 2010, prefix: 'UrbanPopulation' },
  { image: populationUrban2020, year: 2020, prefix: 'UrbanPopulation' },
  { image: populationUrban2030, year: 2030, prefix: 'UrbanPopulation' },
  
  { image: popUrban_10YearLag2020, year: 2020, prefix: 'UrbanPopulation_10YearLag' },
  { image: popUrban_10YearLag2030, year: 2030, prefix: 'UrbanPopulation_10YearLag' },
  
  { image: NonUrbanPop_10YearLag2020, year: 2020, prefix: 'NonUrbanPopulation_10YearLag' },
  { image: NonUrbanPop_10YearLag2030, year: 2030, prefix: 'NonUrbanPopulation_10YearLag' },
  
  { image: popUrban_20YearLag2020, year: 2020, prefix: 'UrbanPopulation_20YearLag' },
  { image: popUrban_20YearLag2030, year: 2030, prefix: 'UrbanPopulation_20YearLag' },
  
  { image: NonUrbanPop_20YearLag2020, year: 2020, prefix: 'NonUrbanPopulation_20YearLag' },
  { image: NonUrbanPop_20YearLag2030, year: 2030, prefix: 'NonUrbanPopulation_20YearLag' },
  
  { image: popChange_2000_2020, year: '2000-2020', prefix: 'PopChange' },
  { image: popChange_2010_2020, year: '2010-2020', prefix: 'PopChange' },
  { image: popChange_2010_2030, year: '2010-2030', prefix: 'PopChange' }, 
  { image: popChange_2020_2030, year: '2020-2030', prefix: 'PopChange' },
  
  { image: c1PopChange2000_2020, year: '2000-2020', prefix: 'c1UrbanPopChange' },
  { image: c1PopChange2010_2020, year: '2010-2020', prefix: 'c1UrbanPopChange' },
  { image: c1PopChange2010_2030, year: '2010-2030', prefix: 'c1UrbanPopChange' }, 
  { image: c1PopChange2020_2030, year: '2020-2030', prefix: 'c1UrbanPopChange' },
  
  { image: c2PopChange2000_2020, year: '2000-2020', prefix: 'c2UrbanPopChange' },
  { image: c2PopChange2010_2020, year: '2010-2020', prefix: 'c2UrbanPopChange' },
  { image: c2PopChange2010_2030, year: '2010-2030', prefix: 'c2UrbanPopChange' }, 
  { image: c2PopChange2020_2030, year: '2020-2030', prefix: 'c2UrbanPopChange' },
  
  { image: c3PopChange2000_2020, year: '2000-2020', prefix: 'c3UrbanPopChange' },
  { image: c3PopChange2010_2020, year: '2010-2020', prefix: 'c3UrbanPopChange' },
  { image: c3PopChange2010_2030, year: '2010-2030', prefix: 'c3UrbanPopChange' }, 
  { image: c3PopChange2020_2030, year: '2020-2030', prefix: 'c3UrbanPopChange' }
];

// Process and export data for each region and raster
print('===== PROCESSING ZONAL STATISTICS BY REGION =====');

// Prioritize certain rasters for immediate processing
var priorityRasters = rasters.filter(function(r) {
  return r.prefix === 'Population' || r.prefix === 'UrbanPopulation';
});

// Process priority rasters first 
print('Processing priority datasets...');
allRegions.forEach(function(region) {
  priorityRasters.forEach(function(r) {
    var rasterName = r.prefix + r.year;
    processRegionAndExport(region.list, region.name, r.image, r.year, rasterName, r.prefix);
  });
});

// Process remaining rasters if needed
print('To process all remaining datasets, uncomment the code below');
/*
allRegions.forEach(function(region) {
  rasters.forEach(function(r) {
    // Skip priority rasters as they're already processed
    if (r.prefix === 'Population' || r.prefix === 'UrbanPopulation') return;
    
    var rasterName = r.prefix + r.year;
    processRegionAndExport(region.list, region.name, r.image, r.year, rasterName, r.prefix);
  });
});
*/

