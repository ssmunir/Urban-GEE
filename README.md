# Urban-GEE

Urban-GEE is a collection of scripts designed to analyze urbanization patterns using Google Earth Engine (GEE) and various data processing tools. This repository includes JavaScript and Python data aggregation, visualization, and analysis scripts.

---
## Table of Contents
1. [Getting Started](#getting-started)
2. [Scripts Overview](#scripts-overview)
3. [Data and Outputs](#data-and-outputs)
---

## Getting Started

To set up the environment and run the scripts:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ssmunir/Urban-GEE.git
   cd Urban-GEE
   ```

2. **Set up the Python environment:**
   ```bash
   conda env create -f environment.yml
   conda activate urban-gee
   ```

---

## Scripts Overview

### JavaScript Scripts (GEE)
- **`double bin population.js`**: Performs double binning for two years on population data in GEE. Results are saved in `Archive/Double bin data`
- **`urbanization.js`**: Aggregates urbanization data using the SMOD Urban def 1 in GEE. Results are saved in `Archive/Population data def1`
- **`urbanizationV2.js`**: Updated version of `Urbanization.js` using second definition of urbanization.
- **`lag_bin.js`**: Applies population bin from `year1` on `year2` population data in GEE. Results are saved in `data/gen/Lagged Bin population.`
- **`bin.js`**: Bins population data in GEE for a given year. Results are saved in `data/gen/Binned population`.

### Python Scripts
- **`gee_sample_maps.py`**: Generates Der Salam Maps with population and SMOD data. Results are stored in `figures/maps`
- **`heatmaps.py`**: Creates heatmaps for population density combinations between two years. Results are stored in the `figures/population_density_heatmaps`.
- **`heatmaps_popchange.py`**: Creates heatmaps for population change combinations. Results are stored in the `figures/popchange_heatmaps`.
- **`merger.py`**: Script to merge the CSV output from `Urbanization.js` and `UrbanizationV2.js`. 
- **`mergeSSA.py`**: Merges datasets specific to Sub-Saharan Africa.
- **`scatter_plots.py`**: Generates scatter plots for urban change variables. Results are stored `\figures`
- **`population_proportion.py`**: Calculates population proportions from datasets.
- **`regions.py`**: Plots world regions as defined in this research. Results are stored in `figures/maps`
- **`replication_plots.py`**: Reproduces ` Henderson, J. V. & Turner, M. (2020) ` figure 1a and 1b.
- **`replication_plots2.py`**: Reproduces ` Henderson, J. V. & Turner, M. (2020) ` figure 1a for each region over multiple years.
- **`tables.py`**: Generates tables summarizing data analyses. Results are saved at `\tables`

---

## Data and Outputs

1. **Input Data**:
  - `data/gen`: Contains data generated in GEE:
       - `Binned population`: Data in this folder is generated from running the `regionagg.js` script in the `GEE_scripts`             folder. Data stored here is used to create the replication plots for ` Henderson, J. V. & Turner, M. (2020) `                figure 1a and 1b by running `replication_plots.py` from the `scripts_for_figures` folder.
       - `Double bin data`: Data in this folder is generated from running the `Double bin population.js` script in the `GEE_scripts` folder. It is used to create the plots in `figures/Heatmaps/population_density_heatmaps` & `/popchange_heatmaps` by running `heatmaps.py` and `heatmaps_popchange.py` respectively from the `scripts_for_figures` folder.
       - `Lagged Bin population`: Data in this folder is generated from running the `lag_bin.js` script in the `GEE_scripts` folder. It is used to create the plots in `figures/contemporaneous_plot` by running `replication_plots2.py` from the `scripts_for_figures` folder.
   - `figures/` directory.
- **Summary Tables**: Stored in the `tables/` directory.

