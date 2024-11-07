import ee
import geemap.foliumap as geemap
import folium 

# Define the folder containing the CSV files
main_path = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\Data"
results = main_path + r"\Results"

ee.Authenticate()
ee.Initialize(project='urbanization-436918')


### 2010 smod html file of Der salam
Map = geemap.Map(control_scale = True, plugin_Fullscreen=False, plugin_Draw=False, search_control=False, scale_control=False)
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

smod2010 = ee.Image("JRC/GHSL/P2023A/GHS_SMOD/2010").select('smod_code');
Map.addLayer(smod2010, {}, "Degree of Urbanization 2010")
Map.add_legend(title="Degree of Urbanization 2010", legend_dict = legend_dict, position="bottomright", draggable=False)


Map.to_html(results + r"\map2010.html")

### 2020 smod html file of Der salam
Map = geemap.Map(control_scale = True, plugin_Fullscreen=False, plugin_Draw=False, search_control=False, scale_control=False)
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

smod2010 = ee.Image("JRC/GHSL/P2023A/GHS_SMOD/2020").select('smod_code');
Map.addLayer(smod2010, {}, "Degree of Urbanization 2020")
Map.add_legend(title="Degree of Urbanization 2020", legend_dict = legend_dict, position="bottomright", draggable=False)


Map.to_html(results + r"\map2020.html")

# basemap of Der salam 
Map = geemap.Map(control_scale = True, plugin_Fullscreen=False, plugin_Draw=False, search_control=False, scale_control=False)
Map.add_basemap("ROADMAP")
Map.setCenter(39.3, -6.9, 10.499) 
Map.to_html(results + r"\der salam.html")
Map