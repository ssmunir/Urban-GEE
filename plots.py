import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

sns.set_theme(style="whitegrid")
plt.rcParams['axes.labelsize'] = 16

# Define the folder containing the CSV files
main_path = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\Data"
results1 = main_path + r"\Results\urban def 1"
results2 = main_path + r"\Results\urban def 2"

# Read full population data with urban def 1
dt = pd.read_csv(results1 + r"\full_population_data.csv")
del dt["Unnamed: 0"]

# Drop countries with less than 100000 population in 2000
dt = dt.loc[dt['Population2000'] > 100000]

# define function to plot variables

def plot_urban_data(data, x_col, x_label, y_col, y_label, hue_col, size_col, palette="bright", sizes=(10, 500), figsize=(14, 7), save_path=None):
    """
    Plot urban data with separate legends for color and size.

    Parameters:
    - data: DataFrame containing the data to plot.
    - x_col: Column name for the x-axis values (e.g., "urbanGrowthRate").
    - y_col: Column name for the y-axis values (e.g., "shOfUrbanPopinPeri").
    - x_label: x axis label
    - y_label: y axis label
    - hue_col: Column name for the color mapping (e.g., "Region").
    - size_col: Column name for the size mapping (e.g., "Population2000").
    - palette: Color palette for the hue variable.
    - sizes: Tuple for the range of sizes for the size variable.
    - figsize: Tuple for the figure size.
    - save_path: Path to save the plot image (optional).
    """
    # Initialize plot
    plt.figure(figsize=figsize)
    ax = sns.regplot(data=data, x=x_col, y=y_col, scatter=False, ci=None, color="black", line_kws=dict(alpha=0.2))
    scatter = sns.scatterplot(data=data, x=x_col, y=y_col, hue=hue_col, palette=palette, size=size_col, sizes=sizes, ax=ax, alpha=0.7, legend="brief")

    # Labels and layout
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    # Separate legends for color (hue) and size
    handles, labels = scatter.get_legend_handles_labels()

    # Identify indices for hue and size legend titles
    hue_index = labels.index(hue_col)
    size_index = labels.index(size_col)

    # Hue (color) legend
    hue_handles = handles[hue_index + 1:size_index]
    hue_labels = labels[hue_index + 1:size_index]
    hue_legend = plt.legend(hue_handles, hue_labels, bbox_to_anchor=(1, 1), loc='upper left', title=hue_col)
    plt.gca().add_artist(hue_legend)  # Add the hue legend to the plot

    # Size legend
    size_handles = handles[size_index + 1:]
    size_labels = labels[size_index + 1:]
    plt.legend(size_handles, size_labels, bbox_to_anchor=(1.05, 0.6), loc='upper left', title="Population in Millions", labelspacing=1.2)

    plt.tight_layout()

    # Save plot if a path is provided
    if save_path:
        plt.savefig(save_path)
    
    plt.show()

# Usage example:
#plot_urban_data(data=dt, x_col="urbanGrowthRate", y_col="shOfUrbanPopinPeri", hue_col="Region", size_col="sqPopulation2000", save_path=results1 + r"\Urban Growth Rate vs Share of Urban Population on Periphery.png")


# ------------------------------------ figures generated from population data 1 with urban >= 22 ---------------------------------#

### define plot variables 2010 - 2020
dt["UrbpopChange"] = dt["UrbanPopulation2020"] - dt["UrbanPopulation2010"]
dt["shOfUrbanPopinPeri"] = dt["UrbanPopulation_10YearLag2020"]/dt["UrbanPopulation2020"]
dt["urbanGrowthRate"] = dt["UrbpopChange"]/dt["UrbanPopulation2010"]
dt["shOfPopUrban2010"] = dt["UrbanPopulation2010"]/dt["Population2010"]
# size parameter = square root of population in 2000
dt["sqPopulation2000"] = np.sqrt(dt["Population2000"])

# Plot 1 Urban Growth Rate vs Share of Urban Population on Periphery
plot_urban_data(data=dt, x_col="urbanGrowthRate", y_col="shOfUrbanPopinPeri",x_label="Urban Growth Rate", y_label="Share of Urban Population on the Periphery", hue_col="Region", size_col="sqPopulation2000", save_path=results1 + r"\Urban Growth Rate vs Share of Urban Population on Periphery.png")

# Plot 2 Urban Share in 2010 vs Share of Urban Population on Periphery
plot_urban_data(data=dt, x_col="shOfPopUrban2010", y_col="shOfUrbanPopinPeri",x_label="Share of urban population in 2010", y_label="Share of Urban Population on the Periphery", hue_col="Region", size_col="sqPopulation2000", save_path=results1 + r"\Share of urban population in 2010 vs Share of Urban Population on Periphery.png")

# Plot 3  Urban Growth Rate vs Share of Urban Population in 2010
plot_urban_data(data=dt, x_col="shOfPopUrban2010", y_col="urbanGrowthRate", x_label="Share of urban population in 2010", y_label="Urban Growth Rate", hue_col="Region", size_col="sqPopulation2000", save_path=results1 + r"\Urban Growth Rate vs Share of urban population in 2010.png")



# Axis definition
#popchange_urban2020_noturban2010 = c2UrbanPopChange_2010-2020
# popchange_urban2020_urban2010 = c3UrbanPopChange_2010-2020
y_axis = (dt["c2UrbanPopChange_2010-2020"])/(dt["c2UrbanPopChange_2010-2020"] + dt["c3UrbanPopChange_2010-2020"])
pop2010_urban2020 = dt["UrbanPopulation2020"] - dt["c2UrbanPopChange_2010-2020"] - dt["c3UrbanPopChange_2010-2020"]
x_axis = (dt["c2UrbanPopChange_2010-2020"] + dt["c3UrbanPopChange_2010-2020"])/pop2010_urban2020


# Plot 4  Urban Growth Rate vs Urban pop change on pp as share of current urban change
plot_urban_data(data=dt, x_col=x_axis, y_col=y_axis, x_label="Total growth rate for current urban area", y_label="Urban pop change on periphery as share of current urban change", hue_col="Region", size_col="sqPopulation2000", save_path=results1 + r"\Urban Growth Rate vs Urban pop change on pp as share of current urban change.png")

# Plot 5  Share of population that is urban 2010 vs Urban pop change on pp as share of current urban change
plot_urban_data(data=dt, x_col="shOfPopUrban2010", y_col=y_axis, x_label="Share of urban population in 2010", y_label="Urban pop change on periphery as share of current urban change", hue_col="Region", size_col="sqPopulation2000", save_path=results1 + r"\Share of urban population in 2010 vs Urban pop change on pp as share of current urban change.png")

# Plot 6  Share of population that is urban 2010 vs Urban pop change on pp as share of current urban change
plot_urban_data(data=dt, x_col="shOfPopUrban2010", y_col=x_axis, x_label="Share of urban population in 2010", y_label="Total growth rate for current urban area", hue_col="Region", size_col="sqPopulation2000", save_path=results1 + r"\Share of urban population in 2010 vs Total growth rate for current urban area.png")

print('Results for urban def 1 saved in ' + results1)





# ------------------------------------ Figures generated from population data 2 with urban >= 21 ---------------------------------#
# Read full population data
dt = pd.read_csv(results2 + r"\full_population_data.csv")

# Drop countries with less than 100000 population in 2000
dt = dt.loc[dt['Population2000'] > 100000]
dt["sqPopulation2000"] = np.sqrt(dt["Population2000"])

del dt["Unnamed: 0"]

### define plot variables 2010 - 2020
dt["UrbpopChange"] = dt["UrbanPopulation2020"] - dt["UrbanPopulation2010"]
dt["shOfUrbanPopinPeri"] = dt["UrbanPopulation_10YearLag2020"]/dt["UrbanPopulation2020"]
dt["urbanGrowthRate"] = dt["UrbpopChange"]/dt["UrbanPopulation2010"]
dt["shOfPopUrban2010"] = dt["UrbanPopulation2010"]/dt["Population2010"]
# size parameter = square root of population in 2000
dt["sqPopulation2000"] = np.sqrt(dt["Population2000"])

# Plot 1 Urban Growth Rate vs Share of Urban Population on Periphery
plot_urban_data(data=dt, x_col="urbanGrowthRate", y_col="shOfUrbanPopinPeri",x_label="Urban Growth Rate", y_label="Share of Urban Population on the Periphery", hue_col="Region", size_col="sqPopulation2000", save_path=results2 + r"\Urban Growth Rate vs Share of Urban Population on Periphery.png")

# Plot 2 Urban Share in 2010 vs Share of Urban Population on Periphery
plot_urban_data(data=dt, x_col="shOfPopUrban2010", y_col="shOfUrbanPopinPeri",x_label="Share of urban population in 2010", y_label="Share of Urban Population on the Periphery", hue_col="Region", size_col="sqPopulation2000", save_path=results2 + r"\Share of urban population in 2010 vs Share of Urban Population on Periphery.png")

# Plot 3  Urban Growth Rate vs Share of Urban Population in 2010
plot_urban_data(data=dt, x_col="shOfPopUrban2010", y_col="urbanGrowthRate", x_label="Share of urban population in 2010", y_label="Urban Growth Rate", hue_col="Region", size_col="sqPopulation2000", save_path=results2 + r"\Urban Growth Rate vs Share of urban population in 2010.png")



# Axis definition
#popchange_urban2020_noturban2010 = c2UrbanPopChange_2010-2020
# popchange_urban2020_urban2010 = c3UrbanPopChange_2010-2020
y_axis = (dt["c2UrbanPopChange_2010-2020"])/(dt["c2UrbanPopChange_2010-2020"] + dt["c3UrbanPopChange_2010-2020"])
pop2010_urban2020 = dt["UrbanPopulation2020"] - dt["c2UrbanPopChange_2010-2020"] - dt["c3UrbanPopChange_2010-2020"]
x_axis = (dt["c2UrbanPopChange_2010-2020"] + dt["c3UrbanPopChange_2010-2020"])/pop2010_urban2020


# Plot 4  Urban Growth Rate vs Urban pop change on pp as share of current urban change
plot_urban_data(data=dt, x_col=x_axis, y_col=y_axis, x_label="Total growth rate for current urban area", y_label="Urban pop change on periphery as share of current urban change", hue_col="Region", size_col="sqPopulation2000", save_path=results2 + r"\Urban Growth Rate vs Urban pop change on pp as share of current urban change.png")

# Plot 5  Share of population that is urban 2010 vs Urban pop change on pp as share of current urban change
plot_urban_data(data=dt, x_col="shOfPopUrban2010", y_col=y_axis, x_label="Share of urban population in 2010", y_label="Urban pop change on periphery as share of current urban change", hue_col="Region", size_col="sqPopulation2000", save_path=results2 + r"\Share of urban population in 2010 vs Urban pop change on pp as share of current urban change.png")

# Plot 6  Share of population that is urban 2010 vs Urban pop change on pp as share of current urban change
plot_urban_data(data=dt, x_col="shOfPopUrban2010", y_col=x_axis, x_label="Share of urban population in 2010", y_label="Total growth rate for current urban area", hue_col="Region", size_col="sqPopulation2000", save_path=results2 + r"\Share of urban population in 2010 vs Total growth rate for current urban area.png")

print('Results for urban def 2 saved in ' + results2)






























