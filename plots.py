import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style="whitegrid")\

# Define the folder containing the CSV files
main_path = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\Data"
results1 = main_path + r"\Results\urban def 1"
results2 = main_path + r"\Results\urban def 2"

# Read full population data
dt = pd.read_csv(results1 + r"\full_population_data.csv")

# Drop countries with less than 100000 population in 2000
dt = dt.loc[dt['Population2000'] > 100000]

del dt["Unnamed: 0"]

# 2010 - 2020 plots


# ------------------------------------ figures generated from population data 1 with urban >= 22 ---------------------------------#

### define plot variables 2020 - 2020
dt["UrbpopChange"] = dt["UrbanPopulation2020"] - dt["UrbanPopulation2010"]
dt["shOfUrbanPopinPeri"] = dt["UrbanPopulation_10YearLag2020"]/dt["UrbanPopulation2020"]
dt["urbanGrowthRate"] = dt["UrbpopChange"]/dt["UrbanPopulation2010"]
dt["shOfPopUrban2010"] = dt["UrbanPopulation2010"]/dt["Population2010"]

# Plot 1 Urban Growth Rate vs Share of Urban Population on Periphery
plt.figure(figsize=(10, 6))
sns.scatterplot(data=dt, x="urbanGrowthRate", y="shOfUrbanPopinPeri", hue="Region", palette="bright")
plt.xlabel("Urban Growth Rate")
plt.ylabel("Share of Population Population on the Periphery")
plt.title("Urban Growth Rate vs Share of Urban Population on Periphery 2010/2020")
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left', title="Region \n")
plt.tight_layout()
plt.savefig(results1 + r"\Urban Growth Rate vs Share of Urban Population on Periphery.png")
#plt.show()

# -----------------------------------------

# Plot 2 Urban Share in 2010 vs Share of Urban Population on Periphery
plt.figure(figsize=(10, 6))
sns.scatterplot(data=dt, x="shOfPopUrban2010", y="shOfUrbanPopinPeri", hue="Region", palette="bright")
plt.xlabel("Urban Population Share in 2010")
plt.ylabel("Share of Population Population on the Periphery")
plt.title("Urban Population Share in 2010 vs Share of Urban Population on Periphery")
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left', title="Region \n")
plt.tight_layout()
plt.savefig(results1 + r"\Urban Share in 2010 vs Share of Urban Population on Periphery.png")
#plt.show()

# --------------------------------------------

# Plot 3  Urban Growth Rate vs Share of Urban Population on Periphery
plt.figure(figsize=(10, 6))

sns.scatterplot(data=dt, y="urbanGrowthRate", x="shOfPopUrban2010", hue="Region", palette="bright")
plt.xlabel("Urban Growth Rate")
plt.ylabel("Urban Population Share in 2010")
plt.title("Urban Growth Rate vs Urban Population Share in 2010")
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left', title="Region \n")
plt.tight_layout()
plt.savefig(results1 + r"\Urban Growth Rate vs Urban Population Share in 2010.png")
#plt.show()

print('Results saved in ' + results1)


# Read full population data
dt = pd.read_csv(results2 + r"\full_population_data.csv")

# Drop countries with less than 100000 population in 2000
dt = dt.loc[dt['Population2000'] > 100000]

del dt["Unnamed: 0"]


# ------------------------------------ Figures generated from population data 2 with urban >= 21 ---------------------------------#
# Axis definition

#popchange_urban2020_noturban2010 = c2UrbanPopChange_2010-2020

# popchange_urban2020_urban2010 = c3UrbanPopChange_2010-2020

# Plot 1  Urban Growth Rate vs Urban pop change on pp as share of current urban change
y_axis = (dt["c2UrbanPopChange_2010-2020"])/(dt["c2UrbanPopChange_2010-2020"] + dt["c3UrbanPopChange_2010-2020"])
pop2010_urban2020 = dt["UrbanPopulation2020"] - dt["c2UrbanPopChange_2010-2020"] - dt["c3UrbanPopChange_2010-2020"]
x_axis = (dt["c2UrbanPopChange_2010-2020"] + dt["c3UrbanPopChange_2010-2020"])/pop2010_urban2020
plt.figure(figsize=(10, 6))

sns.scatterplot(data=dt, y=y_axis, x=x_axis, hue="Region", palette="bright")
plt.xlabel("Total growth rate for current urban area")
plt.ylabel("Urban pop change on pp as share of current urban change")
plt.title("Urban Growth Rate vs Urban pop change on pp as share of current urban change")
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left', title="Region \n")
plt.tight_layout()
plt.savefig(results2 + r"\Urban Growth Rate vs Urban pop change on pp as share of current urban change.png")
#plt.show()



# Plot 2  Share of population that is urban 2010 vs Urban pop change on pp as share of current urban change
x_axis = dt["UrbanPopulation2010"]/dt["Population2010"]
plt.figure(figsize=(10, 6))

sns.scatterplot(data=dt, y=y_axis, x=x_axis, hue="Region", palette="bright")
plt.xlabel("Share of population that is urban 2010")
plt.ylabel("Urban pop change on pp as share of current urban change")
plt.title("Share of population that is urban 2010 vs Urban pop change on pp as share of current urban change")
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left', title="Region \n")
plt.tight_layout()
plt.savefig(results2 + r"\Share of population that is urban 2010 vs Urban pop change on pp as share of current urban change.png")
#plt.show()


# Plot 3  Share of population that is urban 2010 vs Urban pop change on pp as share of current urban change
dt["urbanPopChange"] = dt["UrbanPopulation2020"] - dt["UrbanPopulation2010"]
y_axis =  dt["urbanPopChange"]/dt["UrbanPopulation2010"] 
x_axis = dt["UrbanPopulation2010"]/dt["Population2010"]
plt.figure(figsize=(10, 6))

sns.scatterplot(data=dt, y=y_axis, x=x_axis, hue="Region", palette="bright")
plt.xlabel("Share of population that is urban 2010")
plt.ylabel("total growth rate for current urban area")
plt.title("Share of population that is urban 2010 vs total growth rate for current urban area")
plt.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left', title="Region \n")
plt.tight_layout()
plt.savefig(results2 + r"\Share of population that is urban 2010 vs total growth rate for current urban area.png")
#plt.show()

print('Results saved in ' + results2)