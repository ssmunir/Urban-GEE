import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

if os.getlogin() == "tanner_regan":
    bindata=r"C:\Users\tanner_regan\Documents\GitHub\Urban-GEE\data\gen\Double bin data/" 
    heatmaps=r"C:\Users\tanner_regan\Documents\GitHub\Urban-GEE\figures\Heatmaps"
elif os.getlogin() == "auuser":
    bindata = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\data\gen\Double bin data/"
    heatmaps = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\figures\Heatmaps/"
else: raise ValueError('Path not correctly specified for this computer.')

def generate_population_shift_plot(file_path, output_folder, bin1="bin1980", bin2="bin2020", year1="1980", year2="2020",pop_sum2 = "pop2020_sum", pop_sum1 = "pop1980_sum"):
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
    region_name = os.path.basename(file_path).replace("_Aggregated.csv", "").replace("_", " ")
    
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Define dynamic density bin edges based on data range
    max_density = df[bin2].max()
    bin_edges = np.arange(0, max_density + 1000, 1000)  
    
    # Calculate cumulative 2020 population for each density threshold
    df_sorted = df.sort_values(by=bin2, ascending=False)
    df_sorted["Cumulative_2020_Pop"] = df_sorted[pop_sum2].cumsum()
    
    # Prepare plotting data
    x_values = bin_edges  # Include zero for the first bin
    shifts = [0, 2500, 5000]  # Include shift 0 for first bin
    proportions = {shift: [] for shift in shifts}
    
    for x in x_values:
        total_pop_x = df_sorted.loc[df_sorted[bin2] > x, pop_sum2].sum()
        
        for shift in shifts:
            if x < shift:
                proportions[shift].append(np.nan)  # Leave missing values for x < shift
            else:
                pop_x_shift = df_sorted.loc[(df_sorted[bin2] > x) & (df_sorted[bin1] <= x - shift), pop_sum2].sum()
                proportions[shift].append(pop_x_shift / total_pop_x if total_pop_x > 0 else np.nan)
    
    # Plot
    plt.figure(figsize=(13, 9))
    for shift in shifts:
        plt.plot(x_values, proportions[shift], label=f"Threshold: x-{shift}")
    
    plt.xlabel("Population Density (people per sqkm)")
    plt.ylabel(f"{year2} population share above density x on land below threshold in {year1}")
    #plt.title(f"Population Shift Proportions: {region_name}")
    plt.legend()
    # Force y-axis to range from 0 to 1 and x-axis 0 to 20000
    plt.ylim(0, 1)
    plt.xlim(0, 20000)
    
    plt.grid()
    
    # Save the plot
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f"{region_name}_PopulationShift.png")
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()
    
    print(f"Saved: {output_file}")
    
    
region = [r"\Sub_Saharan_Africa_Aggregated.csv", r"\South_Asia_Aggregated.csv", r"\Latin_America_and_Caribbean_Aggregated.csv", 
          r"\East_Asia_and_Pacific_Aggregated.csv", r"\Europe_and_Central_Asia_Aggregated.csv", r"\Middle_East_and_North_Africa_Aggregated.csv", 
          r"\North_America_Aggregated.csv"]

year1 = r"\1980_2020"
year2 = r"\2000_2020"


for r in region:
    generate_population_shift_plot(file_path=bindata + year1 + r, output_folder= heatmaps + r"\population_shift_plots\1980_2020")
    generate_population_shift_plot(file_path=bindata + year2 + r, output_folder= heatmaps + r"\population_shift_plots\2000_2020", bin1="bin2000", bin2="bin2020", year1="2000")
    generate_population_shift_plot(file_path=bindata + year1 + r, output_folder= heatmaps + r"\population_shift_plots\2020_1980", bin1="bin2020", bin2="bin1980", year2="1980", year1="2020",  pop_sum1= "pop1980_sum")
    generate_population_shift_plot(file_path=bindata + year2 + r, output_folder= heatmaps + r"\population_shift_plots\2020_2000", bin1="bin2020", bin2="bin2000", year1="2020", year2="2000", pop_sum1= "pop2000_sum")
