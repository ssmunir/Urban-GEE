#pip install dask[dataframe]

import os
import dask.dataframe as dd
import pandas as pd
import pycountry_convert as pc 

# Define the folder containing the CSV files
folder_path = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\Population data"

# Loop through all files in the folder and create a list of DataFrames
dataframes = []
for i, filename in enumerate(os.listdir(folder_path)):
    if filename.endswith(".csv"):
        file_path = os.path.join(folder_path, filename)

        # Read the CSV using Dask
        df = dd.read_csv(file_path)

        # Round all population columns to whole numbers (if not the 'country' column)
        for col in df.columns:
            if col != 'country':
                df[col] = df[col].round(0).astype('Int64')  # Round nd convert to integer
        
        # If not the first file, drop the 'country' column.
        if i != 0:
            df = df.drop(columns=['country'])

        dataframes.append(df)

# Concatenate all DataFrames
merged_df = dd.concat(dataframes, axis=1)

# Merge rows with the same country name and sum their values.
merged_df = merged_df.groupby('country').sum().reset_index()

# Compute the final merged result and save it to a new CSV file
output_path = os.path.join(folder_path, 'full_population_data.csv')
#merged_df.compute().to_csv(output_path, index=False)

#print(f'Merged and rounded CSV saved at: {output_path}')

data = merged_df.compute()


def country_to_continent(country_name):
    try:
        country_alpha2 = pc.country_name_to_country_alpha2(country_name)
        country_continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
        country_continent_name = pc.convert_continent_code_to_continent_name(country_continent_code)
        return country_continent_name
    except KeyError as e:
        return "None"
 

# Example
country_name = data['country']
continent_name = [country_to_continent(i) for i in country_name]

data.insert(1, "continent", continent_name)
