import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import matplotlib.colors as mcolors
from matplotlib.colors import LogNorm
from matplotlib.colors import TwoSlopeNorm
from matplotlib.colors import FuncNorm


if os.getlogin() == "tanner_regan":
    bindata=r"C:\Users\tanner_regan\Documents\GitHub\Urban-GEE\archive\Double bin data/" 
    heatmaps=r"C:\Users\tanner_regan\Documents\GitHub\Urban-GEE\figures\Heatmaps/popchange_heatmaps/"
elif os.getlogin() == "auuser":
    bindata = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\archive\Double bin data/"
    heatmaps = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\figures\Heatmaps/popchange_heatmaps/"
else: raise ValueError('Path not correctly specified for this computer.')

# Define the custom log transformation function
def norm_twoslope_log(x):
    x = np.asarray(x, dtype=float)  # Ensure input is an array
    result = np.zeros_like(x)  # Initialize with zeros
    result[x >0] = np.log(x[x >0]+1) # Log for positive values
    result[x==0] = 0 # Around zero treat as linear
    result[x <0] = -np.log(np.abs(x[x <0]-1))# log for negative values
    return result

# Define the inverse function for FuncNorm
def inverse_norm_twoslope_log(y):
    y = np.asarray(y, dtype=float)
    result = np.zeros_like(y)
    result[y > 0] = np.exp(y[y > 0])-1  # Inverse for positive values
    result[y==0] = 0 # Inverse for zero
    result[y < 0] = -np.exp(-y[y < 0])+1 # Inverse for negative values 
    return result
    
def generate_population_heatmap(source_dir,file_name, output_folder, y1,y2):
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
    region_name = os.path.basename(file_name).replace("_Aggregated.csv", "").replace("_", " ")
    
    file_path=source_dir + y1+"_"+y2+file_name
    output_file=output_folder+ y1+"_"+y2+"/"+f"{region_name}.png"
    
    bin1="bin"+y1
    bin2="bin"+y2
    pop_sum1 = "pop"+y1+"_sum"
    pop_sum2 = "pop"+y2+"_sum"
    dpop='dpop'+y1+'_'+y2


    # Read the CSV file
    df = pd.read_csv(file_path)

    # set the upper limit of the data dynamically
    bupr=30
    df.loc[df[bin1]>(bupr+1)*1000,bin1]=(bupr+1)*1000
    df.loc[df[bin2]>(bupr+1)*1000,bin2]=(bupr+1)*1000
     
    df = df.groupby([bin1, bin2], as_index=False).agg({
            pop_sum2: 'sum', pop_sum1: 'sum'})
    
    #make pop change for each bin (in millions of people) and round to thousands
    df[dpop]=(df[pop_sum2]-df[pop_sum1])/1e6
    df[dpop]=df[dpop].round(3)
    
    # Define bin edges and upper bound labels
    #bin_edges = list(range(0, 31000, 1000)) + [float('inf')]
    bin_labels_upper = [str(i) for i in range(0, (bupr+1)*1000, 1000)]
    # Assign labels dynamically: "0", "(0,1]", "(1,2]", ..., "(29,30]"
    bin_labels =["0"] + [f"({i},{i+1}]" for i in range(0, bupr)] + [">"+str(bupr)]

    #THIS IS REDUNDANT
    # Aggregate population by (1980_bin, 2020_bin)
    #df_grouped = df.groupby([bin1, bin2], observed=True).agg({pop_sum2: "sum"}).reset_index()
    #df_grouped.iat[0,2] = 0.0
    
    #No longer needed
    # Calculate population share
    #total_population = df[pop_sum2].sum()
    #df_grouped["Population_Share"] = df_grouped[pop_sum2] / total_population
    ##df_grouped["Population_Share1"]= np.log(df_grouped["Population_Share"])
    
    #keep only columns needed
    df_grouped=df[[bin1,bin2,dpop]]
    
    # Pivot data for heatmap
    heatmap_data = df_grouped.pivot(index=bin2, columns=bin1, values=dpop)
    abs_max = np.max(heatmap_data) # Find the max absolute value to set symmetric limits

    # Create figure
    fig, ax = plt.subplots(figsize=(13, 9))  # Prevent layout shifting
    ax = sns.heatmap(
        heatmap_data, cmap="vlag_r", square=True,  
        norm=FuncNorm((norm_twoslope_log, inverse_norm_twoslope_log),vmin=-abs_max, vmax=abs_max), 
        cbar=True, cbar_kws={'label': 'Total Population Change (millions)','format':'%4.3f'}
    )
    
    # Add a border around the plot space
    for _, spine in ax.spines.items():
        spine.set_visible(True)
    # Fix axis orientation (lower left should be (0,0))
    ax.invert_yaxis()
    #set the axis range to extend fully
    ax.set_xlim([0, len(bin_labels)])
    ax.set_ylim([0, len(bin_labels)])
    
    # Set ticks for colorbar
    cbar = ax.collections[0].colorbar 
    cbar.ax.tick_params(labelsize=10)
    #cbar.ax.set_position([0.85, 0.15, 0.02, 0.7])  # [left, bottom, width, height]
    if np.log(abs_max)>=1:
        five_values_max=[np.floor(np.exp(t)) for t in np.linspace(0, np.log(abs_max), num=5)] 
        custom_ticks=np.concatenate([five_values_max, [0], [-t for t in five_values_max]])
        cbar.set_ticks(custom_ticks)
        cbar.set_ticklabels([f'{x:6.0f}' for x in custom_ticks])  # Format the ticks to 0 decimal places
    elif np.log(abs_max)<1:
        custom_ticks=np.linspace(-abs_max, abs_max, num=9)
        cbar.set_ticks(custom_ticks)
        cbar.set_ticklabels([f'{x:6.2f}' for x in custom_ticks])  # Format the ticks to 2 decimal places
        
    # Set axis labels and title
    plt.xlabel(f"Thousands of people / sqkm in {y1}")
    plt.ylabel(f"Thousands of people / sqkm in {y2}")
    #plt.title(f"Population Density Change Heatmap: {region_name}")
        
    # Dynamically extract tick labels based on bin range
    x_ticks = [tick+0.5 for tick in range(len(bin_labels))]
    y_ticks = [tick+0.5 for tick in range(len(bin_labels))]
    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels([bin_labels[int(tick)] for tick in y_ticks], rotation=0)
    ax.set_xticklabels([bin_labels[int(tick)] for tick in x_ticks], rotation=45, ha="right")
    
    # Add 45-degree reference line
    ticks = np.arange(len(bin_labels_upper)+2)
    plt.plot(ticks, ticks, color="black", linestyle="--", linewidth=2)

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Save the plot
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()  # Close figure to free memory

    print(f"Saved: {output_file}")


region = [r"\Sub_Saharan_Africa_Aggregated.csv", r"\South_Asia_Aggregated.csv", r"\Latin_America_and_Caribbean_Aggregated.csv", 
          r"\East_Asia_and_Pacific_Aggregated.csv", r"\Europe_and_Central_Asia_Aggregated.csv", r"\Middle_East_and_North_Africa_Aggregated.csv", 
          r"\North_America_Aggregated.csv"]


for r in region:
    generate_population_heatmap(source_dir=bindata, file_name=r, output_folder=heatmaps, y1="1980", y2="2020" )
    generate_population_heatmap(source_dir=bindata, file_name=r, output_folder=heatmaps, y1="2000", y2="2020" )
    
    
    
    
