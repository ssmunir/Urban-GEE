#pip install dask[dataframe]

import os
import dask.dataframe as dd

# Define the folder containing the CSV files
folder_path = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\data"

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

# Compute the final merged result and save it to a new CSV file
output_path = os.path.join(folder_path, 'merged_population_data_rounded.csv')
merged_df.compute().to_csv(output_path, index=False)

print(f'Merged and rounded CSV saved at: {output_path}')
