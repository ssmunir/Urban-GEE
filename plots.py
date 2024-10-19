import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
sns.set_theme(style="whitegrid")
sns.set_palette("tab10")

# Define the folder containing the CSV files
main_path = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\Data"
folder_path = main_path + r"\Population data"
results = main_path + r"\Results"

# Read full population data
dt = pd.read_csv(results + r"\full_population_data.csv")

del dt["Unnamed: 0"]

# 2010 - 2020 plots

### define plot variables
dt["popChange"] = dt["Population2020"] - dt["Population2010"]
dt["urbanPopChange"] = np.abs(dt["UrbanPopulation2020"] - dt["UrbanPopulation2010"])
dt["shOfUrbanPopChange"] = dt["UrbanPopulation_10YearLag2020"]/dt["urbanPopChange"]
dt["shareUrbanPop2010"] = dt["UrbanPopulation2010"]/dt["Population2010"]
dt["urbanGrowthRate"] = dt["urbanPopChange"]/dt["UrbanPopulation2010"]

# Plot 1 Urban growth rate and share of population on pp
plt.figure(figsize=(8, 4))
sns.scatterplot(data=dt, x="urbanGrowthRate", y="shOfUrbanPopChange", hue="Region")
plt.xlabel("Urban Growth Rate")
plt.ylabel("Share of Population Change on Periphery")
plt.title("2010/2020 Figures")
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left', title="Region \n")
plt.tight_layout()
plt.savefig(results + r"\urbanGrRtandShofUrbPopChangePP.png")
#plt.show()

# -----------------------------------------

# Plot 2 Share of population urban in 2010 and share of population on pp
plt.figure(figsize=(8, 4))
sns.scatterplot(data=dt, x="shareUrbanPop2010", y="shOfUrbanPopChange", hue="Region")
plt.xlabel("Share of Population that is Urban in 2010")
plt.ylabel("Share of Population Change on Periphery")
plt.title("2010/2020 Figures")
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left', title="Region \n")
plt.tight_layout()
plt.savefig(results + r"\plot2.png")
#plt.show()

# --------------------------------------------

# Plot 3 
plt.figure(figsize=(8, 4))

sns.scatterplot(data=dt, y="urbanGrowthRate", x="shareUrbanPop2010", hue="Region")
plt.xlabel("Urban Growth Rate")
plt.ylabel("Share of Population that is Urban in 2010")
plt.title("2010/2020 Figures")
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left', title="Region \n")
plt.tight_layout()
plt.savefig(results + r"\plot3.png")
#plt.show()