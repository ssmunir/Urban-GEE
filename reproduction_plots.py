## This script loops through the folder containing region csv and 
## replicates Henderson's figure 1 and 2

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

sns.set_theme(style="whitegrid")
plt.rcParams['axes.labelsize'] = 16
plt.rcParams['font.family'] = 'Verdana'  # Replace 'Verdana' with your desired font
# Data folder

mf = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\Data\Binned population"
pop1980 = mf + r"\pop1980"
pop1990 = mf + r"\pop1990"
pop2000 = mf + r"\pop2000"
pop2010 = mf + r"\pop2010"
pop2020 = mf + r"\pop2020"

years = [pop1980, pop1990, pop2000, pop2010, pop2020]


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
            df = df.iloc[1:].sort_values(by=bin_col).reset_index(drop=True)
            
            # Calculate cumulative population
            df['CumulativePopulation'] = df[pop_sum_col].cumsum()
            
            # Calculate total population
            total_population = df[pop_sum_col].sum()
            df['TotalPopulation'] = total_population
            
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
            df = df.head(200)
            
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

#print(landshare.head(201))


def plot_columns(data, plot_title, output_file=None, x_value=19000):
    """
    Create a line plot for all columns in the dataset with Bins as the index.
    Legend is sorted based on y-values at x=20000 from highest to lowest.

    Parameters:
        data_file (str): Path to the input CSV file.
        plot_title (str): Title for the plot.
        output_file (str, optional): Path to save the output plot. If None, displays the plot.
    """
    
    data = data.head(200)
    # Define line styles and grey-to-black color gradient
    line_styles = ['solid', 'dashed', 'dashed', 'dashdot', (5, (10, 3)), 'solid', 'solid']  # Add more if needed
    colors = ['lightcoral', 'black', 'cadetblue', 'tomato', 'darkseagreen', 'goldenrod', 'slategrey']  # colors
    
    # Initialize the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Dictionary to store lines
    lines_dict = {}
    
    # Iterate through columns and plot each with a different style
    for i, column in enumerate(data.columns):
        if column == "Sub_Saharan_Africa":
            line, = plt.plot(  # Note the comma to unpack the tuple
                data.index, 
                data[column], 
                label=column.replace("_", " ").replace("and", "&"), 
                linestyle=line_styles[i % len(line_styles)],
                color=colors[i % len(colors)],
                linewidth=3
            )
            # Store the line object with its column name
            lines_dict[column] = line
        else:
            line, = plt.plot(  # Note the comma to unpack the tuple
                data.index, 
                data[column], 
                label=column.replace("_", " ").replace("and", "&"), 
                linestyle=line_styles[i % len(line_styles)],
                color=colors[i % len(colors)]
            ) 
            # Store the line object with its column name
            lines_dict[column] = line

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

landshare, popshare = process_and_merge_csv_files(pop2010)
plot_title = "Cumulative share of population by density in 2010"
output_file = pop2010 + r"\Cumulative share of population by density 2010.png"  # Set to None if you want to display the plot
plot_columns(popshare, plot_title, output_file)
