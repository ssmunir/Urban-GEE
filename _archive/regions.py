import geopandas as gpd
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Verdana'  # Set font for the plot

# Define the color mapping
region_colors = {
    "South Asia": "#1f77b4",  # Blue
    "Europe & Central Asia": "#ff7f0e",  # Orange 
    "Middle East & North Africa": "#2ca02c",  # Green
    "Sub-Saharan Africa": "#d62728",  # Red
    "Latin America & Caribbean": "#9467bd",  # Purple
    "East Asia & Pacific": "#8c564b",  # Brown
    "North America": "#e377c2",  # Pink
}


# Get world geometry data
url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
world = gpd.read_file(url)

# Filter out Antarctica
world = world.loc[world['REGION_WB'] != "Antarctica"]

if 'REGION_WB' in world.columns and 'NAME' in world.columns:
    # Assign colors based on the region
    world['color'] = world['REGION_WB'].map(region_colors)

    # Plot the map
    fig, ax = plt.subplots(figsize=(20, 12))
    world.plot(
        color=world['color'],  # Use the predefined colors
        ax=ax
    )

    # Create a custom legend
    handles = [
        plt.Line2D([], [], color='white', marker='o', markerfacecolor=color, label=region)
        for region, color in region_colors.items()
    ]
    ax.legend(
        handles=handles,
        loc=(0.1, 0),  # Adjust legend location
        title="Regions",
        title_fontsize=12,
        fontsize=10,
    )
    ax.axis('off')
    # Save the plot
    plt.savefig(r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\Data\figures\maps\world_regions.png", bbox_inches='tight')
else:
    print("'REGION_WB' or 'NAME' column not found in the dataset.")
