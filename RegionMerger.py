import os
import pandas as pd

def merge_population_data(folder_path, region_name):
    """
    Merges population data from multiple CSV files in the given folder.
    
    Parameters:
        folder_path (str): Path to the folder containing the CSV files.
        region_name (str): Name of the region to be used for naming the output DataFrame.
    
    Returns:
        pd.DataFrame: Merged population data.
        float: Total population sum across all bins.
    """
    # Initialize an empty DataFrame for merging
    merged_data = pd.DataFrame()

    # Loop through all files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".csv"):  # Ensure we only process CSV files
            file_path = os.path.join(folder_path, file_name)
            
            # Load the CSV file
            country_data = pd.read_csv(file_path)
            
            # Ensure 'Bin' and 'PopulationSum' columns exist
            if 'Bin' in country_data.columns and 'PopulationSum' in country_data.columns:
                # Drop negative bins
                country_data = country_data[country_data['Bin'] >= 0]
                
                # Merge bins >= 30000 into a single bin labeled '30000'
                if country_data['Bin'].max() >= 30000:
                    over_30000 = country_data[country_data['Bin'] >= 30000]['PopulationSum'].sum()
                    country_data = country_data[country_data['Bin'] < 30000]
                    country_data = pd.concat([country_data, pd.DataFrame({'Bin': [30000], 'PopulationSum': [over_30000]})])
                
                # Merge with the main DataFrame
                if merged_data.empty:
                    merged_data = country_data
                else:
                    merged_data = pd.merge(
                        merged_data, country_data, on='Bin', how='outer', suffixes=(None, '_drop')
                    )
                    
                    # Handle duplicate columns created during merge
                    merged_data['PopulationSum'] = merged_data.filter(like='PopulationSum').sum(axis=1)
                    merged_data = merged_data[['Bin', 'PopulationSum']]  # Keep only relevant columns

    # Group by Bin and Sum Populations
    final_data = merged_data.groupby('Bin', as_index=False)['PopulationSum'].sum()

    # Print information about the result
    print(f"Merged data for region '{region_name}' contains {len(final_data)} bins.")

    return final_data



sa = merge_population_data(r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\Data\Binned population\SA", "South Asia")
ssa = merge_population_data(r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\Data\Binned population\SSA", "Sub Saharan Africa")
eca = merge_population_data(r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\Data\Binned population\ECA", "Europe & Central Asia")
lac = merge_population_data(r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\Data\Binned population\LAC", "Latin America & Caribbean")
mena = merge_population_data(r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\Data\Binned population\MENA", "Middle East & North Africa")
eap = merge_population_data(r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\Data\Binned population\SSA", "East Asia & Pacific")
#na = merge_population_data(r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\Data\Binned population\SA", "North America")