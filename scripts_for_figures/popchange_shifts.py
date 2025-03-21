import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

if os.getlogin() == "tanner_regan":
    bindata=r"C:\Users\tanner_regan\Documents\GitHub\Urban-GEE\archive\Double bin data/" 
    heatmaps=r"C:\Users\tanner_regan\Documents\GitHub\Urban-GEE\figures\Heatmaps/popchange_shift_plots/"
elif os.getlogin() == "auuser":
    bindata = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\archive\Double bin data/"
    heatmaps = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\figures\Heatmaps/popchange_shift_plots/"
else: raise ValueError('Path not correctly specified for this computer.')

def generate_population_shift_plot(source_dir,file_name, y1,y2):
    """
    Generates a plot showing the proportion of the 2020 population in density bins exceeding given thresholds.
    
    Parameters:
    - file_path (str): Path to the CSV file containing population data.
    - output_folder (str): Directory to save the output plot (default: 'output_plots').
    - bin1 (str): Column name for the density bin in the first year (default: 'bin1980').
    - bin2 (str): Column name for the density bin in the second year (default: 'bin2020').
    - year1 (str): Year corresponding to the first density bin (default: '1980').
    - year2 (str): Year corresponding to the second density bin (default: '2020').
    - pop_sum2 (str): Column name for the population sum in the second year (default: 'pop2020_sum').
    - pop_sum1 (str): Column name for the population sum in the first year (default: 'pop1980_sum').
    Saves:
    - A line plot PNG file in the specified output folder.
    """
    
    # Extract region name from filename
    region_name = os.path.basename(file_name).replace("_Aggregated.csv", "").replace("_", " ")
    
    file_path=source_dir + y1+"_"+y2+file_name
    
    bin1="bin"+y1
    bin2="bin"+y2
    pop_sum1 = "pop"+y1+"_sum"
    pop_sum2 = "pop"+y2+"_sum"
    dpop='dpop'+y1+'_'+y2

    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Define dynamic density bin edges based on data range
    max_density = df[bin2].max()
    bin_edges = np.arange(0, max_density + 1000, 1000)  
    
    #make pop change for each bin (in millions of people) and round to thousands
    df[dpop]=(df[pop_sum2]-df[pop_sum1])/1e6
    df[dpop]=df[dpop].round(3)
    
    # Calculate cumulative 2020 population for each density threshold
    df_sorted = df.sort_values(by=bin2, ascending=False)
    
    # Prepare plotting data
    x_values = bin_edges  # do not Include zero for the first bin
    proportions = []
    for x in x_values:
        total_pop_x = df_sorted.loc[df_sorted[bin2] > x, dpop].sum()
        pop_x_shift = df_sorted.loc[(df_sorted[bin2] > x) & (df_sorted[bin1] <= x), dpop].sum()
        proportions.append(pop_x_shift / total_pop_x if total_pop_x > 0 else np.nan)
    
    
    outdf = pd.DataFrame({'density_bin': x_values, region_name: proportions})
    return outdf
    
def make_plots(proportions_df,output_folder, y1,y2):
    output_file=output_folder+ y1+"_"+y2+".png"
    
    df=proportions_df.loc[proportions_df.density_bin!=0] #drop first bin
    
    #line style dictionary for each region as a list that [style, color, width]
    lsd={   'East Asia and Pacific':       ['solid',"#8c564b",1],
            'Europe and Central Asia':     ['dashed',"#ff7f0e",1],
            'Latin America and Caribbean': ['dashed',"#9467bd",1],
            'Middle East and North Africa':['dashdot',"#2ca02c",1],
            'North America':               [(5, (10, 3)),"#e377c2",1],
            'South Asia':                  ['solid',"#1f77b4",1],
            'Sub Saharan Africa':          ['solid',"#d62728",2]
            }
    # Dictionary to store lines
    lines_dict = {}
    # Iterate through columns and plot each with a different style
    for i, col in enumerate(df.columns.drop('density_bin')):
        line, = plt.plot(  # Note the comma to unpack the tuple
            df.index, df[col], 
            label=col.replace("_", " ").replace("and", "&"), 
            linestyle=lsd[col][0],color=lsd[col][1], linewidth=lsd[col][2]
        )
        # Store the line object with its column name
        lines_dict[col] = line
    # Sort columns based on y-values at x=20000
    x_value=19000
    y_values_at_x = {col: df.loc[df.density_bin==x_value, col].values[0] for col in df.columns.drop('density_bin')}
    sorted_columns = sorted(y_values_at_x.keys(), key=lambda x: y_values_at_x[x], reverse=True)
    # Create sorted handles and labels for legend
    sorted_handles = [lines_dict[col] for col in sorted_columns]
    sorted_labels = [col.replace("_", " ").replace("and", "&") for col in sorted_columns]

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))
    # Plot each region with its corresponding line style, color, and width
    for region in df.columns:
        if region != 'density_bin':  # Skip the 'density_bin' column
            style, color, width = lsd[region]  # Get the style, color, and width for the region
            ax.plot(df['density_bin'], df[region], label=region, linestyle=style, color=color, linewidth=width)
    
    # Add sorted legend
    ax.legend(sorted_handles, sorted_labels, title="Regions", loc='lower right', fontsize=10)
    
    # Dynamically extract tick labels based on bin range
    ax.set_yticks([y/10 for y in range(0,11)])
    x_ticks = [tick for tick in df['density_bin']]
    ax.set_xticks(x_ticks)
    bin_labels=[int(tick/1000) for tick in x_ticks]
    bin_labels = [f"({i-1},{i}]" for i in bin_labels[:-1]] + [">"+str(bin_labels[-1])]
    ax.set_xticklabels([b_lbl for b_lbl in bin_labels], rotation=45, ha="right")

    plt.xlabel("Population Density (people per sqkm)")
    plt.ylabel(f"Share pop. change on land with {y2} density>x where {y1} density<x")
    #plt.title(f"Population Shift Proportions: {region_name}")
    plt.legend()
    # Force y-axis to range from 0 to 1 and x-axis 0 to 20000
    plt.ylim(0, 1)
    plt.xlim(0, 30000)
    plt.grid()
    
    # Save the plot
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f"Popchange_shift_{y1}_{y2}.png")
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()
    
    print(f"Saved: {output_file}")
    
    
region = [r"\Sub_Saharan_Africa_Aggregated.csv", r"\South_Asia_Aggregated.csv", r"\Latin_America_and_Caribbean_Aggregated.csv", 
          r"\East_Asia_and_Pacific_Aggregated.csv", r"\Europe_and_Central_Asia_Aggregated.csv", r"\Middle_East_and_North_Africa_Aggregated.csv", 
          r"\North_America_Aggregated.csv"]


#do for 1980 to 2020
dfs=[generate_population_shift_plot(source_dir=bindata, file_name=r, y1="1980", y2="2020" ) for r in region]
merged_df = dfs[0]
for df in dfs[1:]:
    merged_df = pd.merge(merged_df, df,on='density_bin',how='outer')
make_plots(proportions_df=merged_df,output_folder=heatmaps, y1="1980", y2="2020")
    

#do for 2000 to 2020
dfs=[generate_population_shift_plot(source_dir=bindata, file_name=r, y1="2000", y2="2020" ) for r in region]
merged_df = dfs[0]
for df in dfs[1:]:
    merged_df = pd.merge(merged_df, df,on='density_bin',how='outer')
make_plots(proportions_df=merged_df,output_folder=heatmaps, y1="2000", y2="2020")

