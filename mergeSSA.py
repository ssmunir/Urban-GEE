import pandas as pd
import os

def merge_datasets(file1, file2, bin1="bin1980", bin2="bin2020", output_file=""):
    """
    Merges two datasets and aggregates by (bin1, bin2) summing population and bin count.

    Parameters:
    - file1 (str): Path to the first CSV file.
    - file2 (str): Path to the second CSV file.
    - output_file (str): Path to save the merged and aggregated dataset.

    Saves:
    - A merged and aggregated CSV file.
    """
    # Load the two CSV files
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Merge the two datasets
    df_combined = pd.concat([df1, df2], ignore_index=True)

    # Aggregate by (bin1980, bin2020) summing population and bin count
    df_aggregated = df_combined.groupby([bin1, bin2], observed=True).agg({
        "pop2020_sum": "sum",
        "pixel_count": "sum"
    }).reset_index()

    # Save the merged dataset
    df_aggregated.to_csv(output_file, index=False)

    print(f"Merged dataset saved as {output_file}")

# Example usage
main_path = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\Data\Double bin data"
"""
merge_datasets(file1 = main_path + r"\1980_2020\ssa split file\Sub_Saharan_Africa_Aggregated.csv",
               file2 = main_path + r"\1980_2020\ssa split file\Sub_Saharan_Africa2_Aggregated.csv",
               output_file=main_path + r"\1980_2020\Sub_Saharan_Africa_Aggregated.csv")
"""
merge_datasets(file1 = main_path + r"\2000_2020\ssa split file\Sub_Saharan_Africa_Aggregated.csv",
               file2 = main_path + r"\2000_2020\ssa split file\Sub_Saharan_Africa2_Aggregated.csv",
               output_file = main_path + r"\2000_2020\Sub_Saharan_Africa_Aggregated.csv", bin1="bin2000")
