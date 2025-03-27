import ee
import geemap.foliumap as geemap
import folium 
import json
import geopandas as gpd
#4/1AeanS0ansSRPxkqm08oP97fw73spVMXXSBhF6uqQ1ok6TORlBI4f6N82GlQ

ee.Authenticate()
ee.Initialize(project='urbanization-436918')

# Define the folder containing the CSV files
main_path = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE"
results = main_path + r"\figures\maps"

### 2000 smod html file of Der salam
Map = geemap.Map(control_scale=True, plugin_Fullscreen=False, plugin_Draw=False, search_control=False, scale_control=False)
Map.setCenter(39.3, -6.9, 10.499)
legend_dict = {
    "30 Urban Centre": "#ff0000",
    "23 Dense Urban Cluster": "#663300",
    "22 Semi-dense Urban Cluster": "#996600",
    "21 Suburban or Peri-urban": "#ffff00",
    "13 Rural Cluster": "#006600", 
    "12 Low Density Rural": "#99cc00",
    "11 Very Low Density Rural": "#ccff99",
    "10 Water": "#66c2ff"
}   

smod2000 = ee.Image("JRC/GHSL/P2023A/GHS_SMOD/2000").select('smod_code')
Map.add_basemap("ROADMAP")
Map.addLayer(smod2000, {}, "Degree of Urbanization 2000")
Map.add_legend(title="Degree of Urbanization 2000", legend_dict=legend_dict, position="bottomright", draggable=False)
Map.to_html(results + r"\map2000.html")

### 2010 smod html file of Der salam
Map = geemap.Map(control_scale=True, plugin_Fullscreen=False, plugin_Draw=False, search_control=False, scale_control=False)
Map.setCenter(39.3, -6.9, 10.499)
legend_dict = {
    "30 Urban Centre": "#ff0000",
    "23 Dense Urban Cluster": "#663300",
    "22 Semi-dense Urban Cluster": "#996600",
    "21 Suburban or Peri-urban": "#ffff00",
    "13 Rural Cluster": "#006600", 
    "12 Low Density Rural": "#99cc00",
    "11 Very Low Density Rural": "#ccff99",
    "10 Water": "#66c2ff"
}   

smod2010 = ee.Image("JRC/GHSL/P2023A/GHS_SMOD/2010").select('smod_code')
Map.add_basemap("ROADMAP")
Map.addLayer(smod2010, {}, "Degree of Urbanization 2010")
Map.add_legend(title="Degree of Urbanization 2010", legend_dict=legend_dict, position="bottomright", draggable=False)
Map.to_html(results + r"\map2010.html")

### 2020 smod html file of Der salam
Map = geemap.Map(control_scale=True, plugin_Fullscreen=False, plugin_Draw=False, search_control=False, scale_control=False)
Map.setCenter(39.3, -6.9, 10.499)
legend_dict = {
    "30 Urban Centre": "#ff0000",
    "23 Dense Urban Cluster": "#663300",
    "22 Semi-dense Urban Cluster": "#996600",
    "21 Suburban or Peri-urban": "#ffff00",
    "13 Rural Cluster": "#006600", 
    "12 Low Density Rural": "#99cc00",
    "11 Very Low Density Rural": "#ccff99",
    "10 Water": "#66c2ff"
}   

smod2020 = ee.Image("JRC/GHSL/P2023A/GHS_SMOD/2020").select('smod_code')
Map.add_basemap("ROADMAP")
Map.addLayer(smod2020, {}, "Degree of Urbanization 2020")
Map.add_legend(title="Degree of Urbanization 2020", legend_dict=legend_dict, position="bottomright", draggable=False)
Map.to_html(results + r"\map2020.html")

# Basemap of Der salam 
Map = geemap.Map(control_scale=True, plugin_Fullscreen=False, plugin_Draw=False, search_control=False, scale_control=False)
Map.add_basemap("ROADMAP")
Map.setCenter(39.3, -6.9, 10.499) 
Map.to_html(results + r"\der salam.html")

###########################################################
# New section: Population Density Plots with 6 Categories
###########################################################

def preprocess_population(pop_image):
    """
    Replace negative values with 0, aggregate to ~1km resolution,
    and reproject the image to 1km scale.
    """
    return (pop_image.where(pop_image.lt(0), 0)
            .reduceResolution(reducer=ee.Reducer.sum().unweighted(), maxPixels=1024)
            .reproject(crs=pop_image.projection().atScale(1000)))

# Load and preprocess population images for 2000 and 2020
pop2000_image = preprocess_population(ee.Image("JRC/GHSL/P2023A/GHS_POP/2000"))
pop2010_image = preprocess_population(ee.Image("JRC/GHSL/P2023A/GHS_POP/2010"))
pop2020_image = preprocess_population(ee.Image("JRC/GHSL/P2023A/GHS_POP/2020"))

# Define the SLD style string with six categories.
# The new sixth category (≥ 10000) is set to dark brown (#8B4513).
sld_intervals = (
    '<RasterSymbolizer>'
    '<ColorMap type="intervals" extended="false" >'
    '<ColorMapEntry color="#0000ff" quantity="0" label="0 ﹤ x" opacity="0" />'
    '<ColorMapEntry color="#006600" quantity="100" label="0 ≤ x ﹤ 100" />'
    '<ColorMapEntry color="#99cc00" quantity="500" label="100 ≤ x ﹤ 500" />'
    '<ColorMapEntry color="#ccff99" quantity="1000" label="500 ≤ x ﹤ 1000" />'
    '<ColorMapEntry color="#ffff00" quantity="5000" label="1000 ≤ x ﹤ 5000" />'
    '<ColorMapEntry color="#ff0000" quantity="10000" label="5000 ≤ x ﹤ 10000" />'
    '<ColorMapEntry color="#663300" quantity="999999999" label="≥ 10000" />'
    '</ColorMap>'
    '</RasterSymbolizer>'
)

# Define the legend dictionary for population density.
pop_legend_dict = {
    "0 < pop < 100": "#006600",
    "100 ≤ pop < 500": "#99cc00",
    "500 ≤ pop < 1000":  "#ccff99",
    "1000 ≤ pop < 5000": "#ffff00",
    "5000 ≤ pop < 10000": "#ff0000",
    "≥ 10000": "#663300"
}

# Create and save the population density map for the year 2000
popMap2000 = geemap.Map(control_scale=True, plugin_Fullscreen=False, plugin_Draw=False, search_control=False, scale_control=False)
popMap2000.add_basemap("ROADMAP")
popMap2000.setCenter(39.3, -6.9, 10.499)
popMap2000.addLayer(pop2000_image.sldStyle(sld_intervals), {}, "Population density 2000")
popMap2000.add_legend(title="Pop. density per sqkm (2000)", legend_dict=pop_legend_dict, position="bottomright", draggable=False)
popMap2000.to_html(results + r"\pop_map2000.html")


# Create and save the population density map for the year 2010
popMap2010 = geemap.Map(control_scale=True, plugin_Fullscreen=False, plugin_Draw=False, search_control=False, scale_control=False)
popMap2010.add_basemap("ROADMAP")
popMap2010.setCenter(39.3, -6.9, 10.499)
popMap2010.addLayer(pop2010_image.sldStyle(sld_intervals), {}, "Population density 2010")
popMap2010.add_legend(title="Pop. density per sqkm (2010)", legend_dict=pop_legend_dict, position="bottomright", draggable=False)
popMap2010.to_html(results + r"\pop_map2010.html")

# Create and save the population density map for the year 2020
popMap2020 = geemap.Map(control_scale=True, plugin_Fullscreen=False, plugin_Draw=False, search_control=False, scale_control=False)
popMap2020.add_basemap("ROADMAP")
popMap2020.setCenter(39.3, -6.9, 10.499)
popMap2020.addLayer(pop2020_image.sldStyle(sld_intervals), {}, "Population density 2020")
popMap2020.add_legend(title="Pop. density per sqkm (2020)", legend_dict=pop_legend_dict, position="bottomright", draggable=False)
popMap2020.to_html(results + r"\pop_map2020.html")