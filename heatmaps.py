# Load and inspect the structure of the uploaded file
import pandas as pd


import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

file_path = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\Data\Double bin data\North_America_Aggregated.csv"
# Read the CSV file
df = pd.read_csv(file_path)
# Define bin edges and upper bound labels
bin_edges = list(range(0, 31000, 1000)) + [float('inf')]
bin_labels_upper = [str(i+1000) for i in range(0, 30000, 1000)] + [">30000"]

# Convert bins to categorical with defined order
df["Bin_1980"] = pd.cut(df["bin1980"], bins=bin_edges, labels=bin_labels_upper, right=True)
df["Bin_2020"] = pd.cut(df["bin2020"], bins=bin_edges, labels=bin_labels_upper, right=True)

# Aggregate population by (1980_bin, 2020_bin)
df_grouped = df.groupby(["Bin_1980", "Bin_2020"], observed=True).agg({"pop2020_sum": "sum"}).reset_index()

# Calculate population share
total_population = df_grouped["pop2020_sum"].sum()
df_grouped["Population_Share"] = df_grouped["pop2020_sum"] / total_population

# Pivot data for heatmap
heatmap_data = df_grouped.pivot(index="Bin_2020", columns="Bin_1980", values="Population_Share")

# Plot heatmap with updated tick labels
plt.figure(figsize=(10, 8))
ax = sns.heatmap(
    heatmap_data, cmap="Blues", cbar_kws={'label': 'Population Share'}, square=True
)

# Set axis labels
plt.xlabel("1980 Population Density Bins")
plt.ylabel("2020 Population Density Bins")
plt.title("Population Density Change Heatmap: North America")

# Ensure all bin labels appear with upper bounds
ax.set_xticklabels(bin_labels_upper, rotation=45, ha="right")
ax.set_yticklabels(bin_labels_upper, rotation=0)

# Fix axis orientation (lower left should be (0,0))
ax.invert_yaxis()

# Add 45-degree line
ticks = np.arange(len(bin_labels_upper))
plt.plot(ticks, ticks, color="red", linestyle="--", linewidth=2)

# Show plot
plt.show()

