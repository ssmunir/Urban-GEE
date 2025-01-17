## This script loops through the folder containing region csv and 
## replicates Henderson's figure 1 and 2

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.interpolate import interp1d
import numpy as np
import os

sns.set_theme(style="whitegrid")
plt.rcParams['axes.labelsize'] = 16
plt.rcParams['font.family'] = 'Verdana' # Set font for the plot
# Data folder

mf = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\Data\Lagged Bin population"
#mf = r"C:\Users\tanner_regan\Documents\GitHub\Urban-GEE\Data\Binned population"

contemp = [r"\SSA_contemp", r"\NA_contemp", r"\MENA_contemp",
            r"\SA_contemp", r"\LAC_contemp", r"\EAP_contemp", r"\ECA_contemp"]

lag_1980 = [r"\SSA_1980_lag", r"\NA_1980_lag", r"\MENA_1980_lag",
            r"\SA_1980_lag", r"\LAC_1980_lag", r"\EAP_1980_lag", r"\ECA_1980_lag"]

region = ['Sub Saharan Africa', 'North America', 'Middle East and North Africa', 
          'South Asia', 'Latin America and Caribbean', 'East Asia and Pacific', 
          'Europe and Central Asia']

code = ['SSA', 'NA', 'MENA', 'SA', 'LAC', 'EAP', 'ECA']
# Define the color mapping


#line style dictionary for each region as a list that [style, color, width]
lsd={   '1980': ['solid',"#8c564b",1],
        '1990': ['dashed',"#ff7f0e",1],
        '2000': ['dashed',"#9467bd",1],
        '2010': ['dashdot',"#2ca02c",1],
        '2020': [(5, (10, 3)),"#e377c2",1]
        }


def process_and_merge_csv_files(input_folder, bin_col='Bin', pop_sum_col='PopulationSum', cell_count_col='GridcellCount'):
    """
    Read CSV files from a folder, calculate cumulative metrics, limit data to the first 200 rows,
    and generate two separate datasets: one for `CumulativeLandShare` and another for `CumulativeShare`.

    Parameters:
        input_folder (str): Path to the folder containing CSV files.
        landshare_output_file (str): Path to save the merged output CSV file for CumulativeLandShare.
        share_output_file (str): Path to save the merged output CSV file for CumulativeShare.
        bin_col (str): Column name for bins (default is 'Bin').
        pop_sum_col (str): Column name for population sums (default is 'PopulationSum').
        cell_count_col (str): Column name for grid cell counts (default is 'GridCellCount').
    """
    all_landshare_data = []  # List to store CumulativeLandShare DataFrames
    all_share_data = []      # List to store CumulativeShare DataFrames
    
    for file in os.listdir(input_folder):
        if file.endswith('.csv'):
            # Read the CSV file
            file_path = os.path.join(input_folder, file)
            df = pd.read_csv(file_path)
            
            # Group by bin and aggregate sums
            df = df.groupby(bin_col, as_index=False).agg({
                pop_sum_col: 'sum',
                cell_count_col: 'sum'
            })
            
            # Ensure the DataFrame is sorted by bins
            ##WHY drop bin 0? df = df.iloc[1:].sort_values(by=bin_col).reset_index(drop=True)
            df = df.sort_values(by=bin_col).reset_index(drop=True)
            
            # Calculate cumulative population
            df['CumulativePopulation'] = df[pop_sum_col].cumsum()
            
            # Calculate total population
            total_population = df[pop_sum_col].sum()
            
            # Calculate cumulative share of population
            df['CumulativeShare'] = df['CumulativePopulation'] / total_population
            
            # Calculate cumulative cells
            df['CumulativeCells'] = df[cell_count_col].cumsum()
            
            # Calculate total cells
            total_cells = df[cell_count_col].sum()
            df['TotalCells'] = total_cells
            
            # Calculate cumulative land share
            df['CumulativeLandShare'] = df['CumulativeCells'] / total_cells
            
            # Limit to the first 200 rows
            #df = df.head(200)
            
            # Select and rename columns for land share
            landshare_df = df[[bin_col, 'CumulativeLandShare']].rename(columns={
                'CumulativeLandShare': f"{os.path.splitext(file)[0].split('_')[-1]}"
            })
            all_landshare_data.append(landshare_df)
            
            # Select and rename columns for share
            share_df = df[[bin_col, 'CumulativeShare']].rename(columns={
                'CumulativeShare': f"{os.path.splitext(file)[0].split('_')[-1]}"
            })
            all_share_data.append(share_df)
    
    # Merge all DataFrames for land share on the 'Bin' column
    merged_landshare = all_landshare_data[0]
    for df in all_landshare_data[1:]:
        merged_landshare = pd.merge(merged_landshare, df, on=bin_col, how='outer')
    
    # Merge all DataFrames for share on the 'Bin' column
    merged_share = all_share_data[0]
    for df in all_share_data[1:]:
        merged_share = pd.merge(merged_share, df, on=bin_col, how='outer')
        
    return merged_landshare.set_index('Bin'), merged_share.set_index('Bin')




def plot1a(data, plot_title, output_file=None, x_value=19000, x_label =""):
    """
    Create a line plot for all columns in the dataset with Bins as the index.
    Legend is sorted based on y-values at x=20000 from highest to lowest.

    Parameters:
        data_file (str): Path to the input CSV file.
        plot_title (str): Title for the plot.
        output_file (str, optional): Path to save the output plot. If None, displays the plot.
    """

    # Initialize the plot
    fig, ax = plt.subplots(figsize=(13, 9))
    
    # Dictionary to store lines
    lines_dict = {}
    
    # Iterate through columns and plot each with a different style
    for i, col in enumerate(data.columns):
        line, = plt.plot(  # Note the comma to unpack the tuple
            data.index, data[col], 
            label=col.replace("_", " ").replace("and", "&"), 
            linestyle=lsd[col][0],color=lsd[col][1], linewidth=lsd[col][2]
        )
        # Store the line object with its column name
        lines_dict[col] = line

    """# Sort columns based on y-values at x=20000
    y_values_at_x = {col: data.loc[x_value, col] for col in data.columns if x_value in data.index}
    sorted_columns = sorted(y_values_at_x.keys(), key=lambda x: y_values_at_x[x], reverse=True)
    
    # Create sorted handles and labels for legend
    sorted_handles = [lines_dict[col] for col in sorted_columns]
    sorted_labels = [col.replace("_", " ").replace("and", "&") for col in sorted_columns]
    
    # Add sorted legend
    ax.legend(sorted_handles, sorted_labels, title="Years", loc='lower right', fontsize=10)
    """
    # Customize the plot
    plt.title(plot_title, fontsize=16)
    plt.xlabel(x_label, fontsize=14)
    plt.ylabel('Share of total population', fontsize=14)
    ax.legend(title="Years", loc='lower right', fontsize=10)
    # Turn on the minor ticks, which are required for the minor grid
    ax.minorticks_on()

    # Customize the major grid
    ax.grid(which='major', linestyle='-', linewidth='0.5', color='black')

    # Customize the minor grid
    ax.grid(which='minor', linestyle=':', linewidth='0.25', color='gray')

    
    
    
    # Customize x-axis ticks
    plt.xticks(ticks=[0, 5000, 10000, 15000, 20000, 25000, 30000])
    plt.xlim(0, 30000)
    plt.ylim(0, 1)
    
    # Save or display the plot
    if output_file:
        plt.savefig(output_file, bbox_inches='tight')
        print(f"Plot saved to {output_file}")
    else:
        plt.show()

# Contemporous plots
for dt, reg, c in zip(contemp, region, code):
    file = mf + dt
    landshare, popshare = process_and_merge_csv_files(file)
    plot_title = " "
    output_file = file + f"\Cumulative share of population by density_{c}.png"  # Set to None if you want to display the plot
    plot1a(popshare, plot_title, output_file, x_label="Contemporaneous Population / Square Kilometer")

# 1980 lagged plots
for dt, reg, c in zip(lag_1980, region, code):
    file = mf + dt
    landshare, popshare = process_and_merge_csv_files(file, pop_sum_col='TotalPopulationSum', cell_count_col='TotalCellCount')
    plot_title = " "
    output_file = file + f"\Cumulative share of population by density in 1980_{c}.png"  # Set to None if you want to display the plot
    plot1a(popshare, plot_title, output_file, x_label="Population / Square Kilometer in 1980")
