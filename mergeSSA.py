import pandas as pd
import os

main_path = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\Data\Double bin data"


# Load the two CSV files
file1 = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\Data\Double bin data\ssa split file\Sub_Saharan_Africa_Aggregated.csv"
file2 = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\Data\Double bin data\ssa split file\Sub_Saharan_Africa2_Aggregated.csv"

df1 = pd.read_csv(file1)
df2 = pd.read_csv(file2)

# Merge the two datasets
df_combined = pd.concat([df1, df2], ignore_index=True)

# Aggregate by (bin1980, bin2020) summing population and bin count
df_aggregated = df_combined.groupby(["bin1980", "bin2020"], observed=True).agg({
    "pop2020_sum": "sum",
    "pixel_count": "sum"
}).reset_index()

# Save the merged dataset
output_file = main_path + r"\Sub_Saharan_Africa_Aggregated.csv"
df_aggregated.to_csv(output_file, index=False)

print(f"Merged dataset saved as {output_file}")
