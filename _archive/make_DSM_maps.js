/************************************************************
 * Load datasets and setup initial variables
 ************************************************************/
var population2000 = ee.Image("JRC/GHSL/P2023A/GHS_POP/2000");
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
var pop2000 = preprocessPopulation(population2000);
var pop2020 = preprocessPopulation(population2020);

/************************************************************
 * Add to map
 ************************************************************/
var sld_intervals =
  '<RasterSymbolizer>' +
    '<ColorMap type="intervals" extended="false" >' +
      '<ColorMapEntry color="#0000ff" quantity="0" label="0 ﹤ x" opacity="0" />' +
      '<ColorMapEntry color="#007f30" quantity="100" label="0 ≤ x ﹤ 100" />' +
      '<ColorMapEntry color="#30b855" quantity="500" label="100 ≤ x ﹤ 500" />' +
      '<ColorMapEntry color="#00ff00" quantity="1000" label="500 ≤ x ﹤ 1000" />' +
      '<ColorMapEntry color="#ffff00" quantity="5000" label="1000 ≤ x ﹤ 5000" />' +
      '<ColorMapEntry color="#ff0000" quantity="10000" label="5000 ≤ x ﹤ 10000" />' +
      '<ColorMapEntry color="#8B4513" quantity="999999999" label="x ≥ 10000" />' +
    '</ColorMap>' +
  '</RasterSymbolizer>';

Map.setCenter(39.27296253336732,-6.824393754199092, 8);
Map.addLayer(pop2020.sldStyle(sld_intervals), {}, 'Population count, 2020');
Map.addLayer(pop2000.sldStyle(sld_intervals), {}, 'Population count, 2000');



/************************************************************
 * Add a legend to map
 ************************************************************/
// set position of panel
var legend = ui.Panel({
  style: {
    position: 'bottom-right',
    padding: '8px 15px'
  }
});
 
// Create legend title
var legendTitle = ui.Label({
  value: 'Pop. density per sqkm',
  style: {
    fontWeight: 'bold',
    fontSize: '18px',
    margin: '0 0 4px 0',
    padding: '0'
    }
});
 
// Add the title to the panel
legend.add(legendTitle);
 
// Creates and styles 1 row of the legend.
var makeRow = function(color, name) {
 
      // Create the label that is actually the colored box.
      var colorBox = ui.Label({
        style: {
          backgroundColor: '#' + color,
          // Use padding to give the box height and width.
          padding: '8px',
          margin: '0 0 4px 0'
        }
      });
 
      // Create the label filled with the description text.
      var description = ui.Label({
        value: name,
        style: {margin: '0 0 4px 6px'}
      });
 
      // return the panel
      return ui.Panel({
        widgets: [colorBox, description],
        layout: ui.Panel.Layout.Flow('horizontal')
      });
};
 
///  Palette with the colors (now 6 entries)
var palette = [
  '007f30',  // 0-100
  '30b855',  // 100-500
  '00ff00',  // 500-1000
  'ffff00',  // 1000-5000
  'ff0000',  // 5000-10000
  '8B4513'   // ≥10000 (new)
];

// Names for each category (also 6 entries)
var names = [
  '0<pop<100',
  '100≤pop<500',
  '500≤pop<1000',
  '1000≤pop<5000',
  '5000≤pop<10000',
  '≥10000'      // new
];

// Add color and and names
for (var i = 0; i < 5; i++) {
  legend.add(makeRow(palette[i], names[i]));
  }  
 
// add legend to map (alternatively you can also print the legend to the console)
Map.add(legend);
