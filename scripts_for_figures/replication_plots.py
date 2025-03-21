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

mf = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\archive\Binned population"
#mf = r"C:\Users\tanner_regan\Documents\GitHub\Urban-GEE\archive\Binned population"
pop1980 = mf + r"\pop1980"
pop1990 = mf + r"\pop1990"
pop2000 = mf + r"\pop2000"
pop2010 = mf + r"\pop2010"
pop2020 = mf + r"\pop2020"

folderList = [pop1980, pop1990, pop2000, pop2010, pop2020]
years = [1980, 1990, 2000, 2010, 2020]


#line style dictionary for each region as a list that [style, color, width]
lsd={   'East_Asia_and_Pacific':       ['solid',"#8c564b",1],
        'Europe_and_Central_Asia':     ['dashed',"#ff7f0e",1],
        'Latin_America_and_Caribbean': ['dashed',"#9467bd",1],
        'Middle_East_and_North_Africa':['dashdot',"#2ca02c",1],
        'North_America':               [(5, (10, 3)),"#e377c2",1],
        'South_Asia':                  ['solid',"#1f77b4",1],
        'Sub_Saharan_Africa':          ['solid',"#d62728",2]
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
                'CumulativeLandShare': f"{os.path.splitext(file)[0]}"
            })
            all_landshare_data.append(landshare_df)
            
            # Select and rename columns for share
            share_df = df[[bin_col, 'CumulativeShare']].rename(columns={
                'CumulativeShare': f"{os.path.splitext(file)[0]}"
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


def plot1a(data, plot_title, output_file=None, x_value=19000):
    """
    Create a line plot for all columns in the dataset with Bins as the index.
    Legend is sorted based on y-values at x=20000 from highest to lowest.

    Parameters:
        data_file (str): Path to the input CSV file.
        plot_title (str): Title for the plot.
        output_file (str, optional): Path to save the output plot. If None, displays the plot.
    """

    # Initialize the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
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

    # Sort columns based on y-values at x=20000
    y_values_at_x = {col: data.loc[x_value, col] for col in data.columns if x_value in data.index}
    sorted_columns = sorted(y_values_at_x.keys(), key=lambda x: y_values_at_x[x], reverse=True)
    
    # Create sorted handles and labels for legend
    sorted_handles = [lines_dict[col] for col in sorted_columns]
    sorted_labels = [col.replace("_", " ").replace("and", "&") for col in sorted_columns]
    
    # Add sorted legend
    ax.legend(sorted_handles, sorted_labels, title="Regions", loc='lower right', fontsize=10)
    
    # Customize the plot
    plt.title(plot_title, fontsize=16)
    plt.xlabel('Population / Square Kilometer', fontsize=14)
    plt.ylabel('Share of total population', fontsize=14)
    plt.grid(True)
    
    # Customize x-axis ticks
    plt.xticks(ticks=[0, 5000, 10000, 15000, 20000])
    plt.xlim(0, 20000)
    plt.ylim(0, 1)
    
    # Save or display the plot
    if output_file:
        plt.savefig(output_file, bbox_inches='tight')
        print(f"Plot saved to {output_file}")
    else:
        plt.show()


def plot1b(data1, data2, plot_title, output_file=None, x_value=98):
    """
    Plot columns from two datasets against each other.

    Parameters:
        data1 (DataFrame): First dataset with 'Bin' as the index.
        data2 (DataFrame): Second dataset with 'Bin' as the index.
        plot_title (str): Title for the plot.
        output_file (str, optional): Path to save the output plot. If None, displays the plot.
    """

    # Initialize the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Dictionary to store lines
    lines_dict = {}
    # Ensure both datasets have the same columns
    common_columns = set(data1.columns).intersection(set(data2.columns))

    for i, col in enumerate(common_columns):
        #print(col)
        #dt1 = data2[data2[col] >= 0.65][col] * 100
        #dt2 = data1[col].loc[data2[data2[col] >= 0.65][col].index]
        dt1 = data2[col] * 100
        dt2 = data1[col]
        dt1.dropna(inplace=True)
        dt2.dropna(inplace=True)
        line, = plt.plot(
            dt1, dt2, 
            label=col.replace("_", " ").replace("and", "&"), 
            linestyle=lsd[col][0],color=lsd[col][1], linewidth=lsd[col][2]
            )     
    
        # Store the line object with its column name
        lines_dict[col] = line
            
    # Customize the plot
    plt.title(plot_title, fontsize=16)
    plt.xlabel('Cumulative population in 3% of land with highest density', fontsize=14)
    plt.ylabel('Share of total population', fontsize=14)
    plt.legend()
    plt.grid(True)
    
    # Customize x-axis ticks
    plt.xticks(ticks=[97, 98, 99, 100])
    plt.xlim(97, 100)
    plt.ylim(0, 1)
    
    # Save or display the plot
    if output_file:
        plt.savefig(output_file, bbox_inches='tight')
        print(f"Plot saved to {output_file}")
    else:
        plt.show()


for dt, year in zip(folderList, years):
    landshare, popshare = process_and_merge_csv_files(dt)
    plot_title = " "
    output_file = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\figures\replicated_plots" + f"\Cumulative share of population by density {year}.png"  # Set to None if you want to display the plot
    plot1a(popshare, plot_title, output_file)
    plot_title = " "
    output_file = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\figures\replicated_plots" + f"\Cumulative percentage of population by land area in the region {year}.png"  # Set to None if you want to display the plot
    plot1b(popshare, landshare, plot_title, output_file)




