import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from matplotlib.colors import LogNorm

if os.getlogin() == "tanner_regan":
    bindata=r"C:\Users\tanner_regan\Documents\GitHub\Urban-GEE\Data\Double bin data/" 
    heatmaps=r"C:\Users\tanner_regan\Documents\GitHub\Urban-GEE\Data\Heatmaps"
elif os.getlogin() == "auuser":
    bindata = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\Data\Double bin data/"
    heatmaps = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\Data\Heatmaps/"
else: raise ValueError('Path not correctly specified for this computer.')


def generate_population_heatmap(file_path, output_folder=heatmaps + r"\population_density_heatmaps", bin1="bin1980", bin2="bin2020", year1="1980", year2="2020"):
    """
    Generates a population density change heatmap from a given CSV file.

    Parameters:
    - file_path (str): Path to the CSV file containing population data.
    - output_folder (str): Directory to save the output heatmap (default: 'output_plots').
    - bin1 (str): Column name for the density bin in the first year (default: 'bin1980').
    - bin2 (str): Column name for the density bin in the second year (default: 'bin2020').
    - year1 (str): Year corresponding to the first density bin (default: '1980').
    - year2 (str): Year corresponding to the second density bin (default: '2020').

    Saves:
    - A heatmap PNG file in the specified output folder.
    """

    # Extract region name from filename
    region_name = os.path.basename(file_path).replace("_Aggregated.csv", "").replace("_", " ")

    # Read the CSV file
    df = pd.read_csv(file_path)

    # set the upper limit of the data dynamically
    bupr=30
    df.loc[df[bin1]>(bupr+1)*1000,bin1]=(bupr+1)*1000
    df.loc[df[bin2]>(bupr+1)*1000,bin2]=(bupr+1)*1000
     
    df = df.groupby([bin1, bin2], as_index=False).agg({
            'pop2020_sum': 'sum','pixel_count': 'sum'})
    
    # Define bin edges and upper bound labels
    #bin_edges = list(range(0, 31000, 1000)) + [float('inf')]
    bin_labels_upper = [str(i) for i in range(0, (bupr+1)*1000, 1000)]
    # Assign labels dynamically: "0", "(0,1]", "(1,2]", ..., "(29,30]"
    bin_labels =["0"] + [f"({i},{i+1}]" for i in range(0, bupr)] + [">"+str(bupr)]

    # Aggregate population by (1980_bin, 2020_bin)
    df_grouped = df.groupby([bin1, bin2], observed=True).agg({"pop2020_sum": "sum"}).reset_index()
    #df_grouped.iat[0,2] = 0.0

    # Calculate population share
    total_population = df_grouped["pop2020_sum"].sum()
    df_grouped["Population_Share"] = df_grouped["pop2020_sum"] / total_population
    #df_grouped["Population_Share1"]= np.log(df_grouped["Population_Share"])
    # Pivot data for heatmap
    heatmap_data = df_grouped.pivot(index=bin2, columns=bin1, values="Population_Share")

    # Create figure
    plt.figure(figsize=(13, 9))
    ax = sns.heatmap(
        heatmap_data, cmap="Blues", square=True,  norm=LogNorm(vmin=0.001, vmax=0.2), 
        cbar_kws={'label': 'Population Share (log scale)','format':'%4.3f'}
    )
    
    # Add a border around the plot space
    for _, spine in ax.spines.items():
        spine.set_visible(True)
    
    # Set axis labels and title
    plt.xlabel(f"Thousands of people / sqkm in {year1}")
    plt.ylabel(f"Thousands of people / sqkm in {year2}")
    #plt.title(f"Population Density Change Heatmap: {region_name}")
    
    # Fix axis orientation (lower left should be (0,0))
    ax.invert_yaxis()

    #set the axis range to extend fully
    ax.set_xlim([0, len(bin_labels)])
    ax.set_ylim([0, len(bin_labels)])
    

    # Dynamically extract tick labels based on bin range
    x_ticks = [tick+0.5 for tick in range(len(bin_labels))]
    y_ticks = [tick+0.5 for tick in range(len(bin_labels))]
    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([bin_labels[int(tick)] for tick in y_ticks], rotation=0)
    ax.set_xticklabels([bin_labels[int(tick)] for tick in x_ticks], rotation=45, ha="right")
    
    # Add 45-degree reference line
    ticks = np.arange(len(bin_labels_upper)+2)
    plt.plot(ticks, ticks, color="red", linestyle="--", linewidth=2)

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Save the plot
    output_file = os.path.join(output_folder, f"{region_name}.png")
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()  # Close figure to free memory

    print(f"Saved: {output_file}")


region = [r"\Sub_Saharan_Africa_Aggregated.csv", r"\South_Asia_Aggregated.csv", r"\Latin_America_and_Caribbean_Aggregated.csv", 
          r"\East_Asia_and_Pacific_Aggregated.csv", r"\Europe_and_Central_Asia_Aggregated.csv", r"\Middle_East_and_North_Africa_Aggregated.csv", 
          r"\North_America_Aggregated.csv"]

year1 = r"\1980_2020"
year2 = r"\2000_2020"

for r in region:
    generate_population_heatmap(file_path=bindata + year1 + r, output_folder=heatmaps + r"\population_density_heatmaps" + year1)
    generate_population_heatmap(file_path=bindata + year2 + r, output_folder=heatmaps + r"\population_density_heatmaps" + year2, bin1="bin2000", bin2="bin2020", year1="2000")