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
Map.setCenter(38.7759, -6.913, 8.5)
legend_dict = {
    "30 Urban Centre": "FF0000",
    "23 Dense Urban Cluster": "FFA500",
    "22 Semi-dense Urban Cluster": "FFD700",
    "21 Suburban or Peri-urban": "ADFF2F",
    "13 Rural Cluster": "32CD32", 
    "12 Low Density Rural": "98FB98",
    "11 Very Low Density Rural": "D3D3D3",
    "10 Water": "87CEEB"
}   

smod2010 = ee.Image("JRC/GHSL/P2023A/GHS_SMOD/2010").select('smod_code');
Map.addLayer(smod2010, {}, "Degree of Urbanization 2010")
Map.add_legend(title="Degree of Urbanization 2010", legend_dict = legend_dict, position="bottomright", draggable=False)


Map.to_html(results + r"\map2010.html")

### 2020 smod html file of Der salam
Map = geemap.Map(control_scale = True, plugin_Fullscreen=False, plugin_Draw=False, search_control=False, scale_control=False)
Map.setCenter(38.7759, -6.913, 8.5)
legend_dict = {
    "30 Urban Centre": "FF0000",
    "23 Dense Urban Cluster": "FFA500",
    "22 Semi-dense Urban Cluster": "FFD700",
    "21 Suburban or Peri-urban": "ADFF2F",
    "13 Rural Cluster": "32CD32", 
    "12 Low Density Rural": "98FB98",
    "11 Very Low Density Rural": "D3D3D3",
    "10 Water": "87CEEB"
}   

smod2010 = ee.Image("JRC/GHSL/P2023A/GHS_SMOD/2020").select('smod_code');
Map.addLayer(smod2010, {}, "Degree of Urbanization 2020")
Map.add_legend(title="Degree of Urbanization 2020", legend_dict = legend_dict, position="bottomright", draggable=False)


Map.to_html(results + r"\map2020.html")

# basemap of Der salam 
Map = geemap.Map(plugin_Fullscreen=False, plugin_Draw=False, search_control=False, scale_control=False)
Map.add_basemap("ROADMAP")
Map.setCenter(38.7759, -6.913, 8.5)
Map.to_html(results + r"\der salam.html")
Map