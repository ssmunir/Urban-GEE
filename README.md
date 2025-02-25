# Urban-GEE

Urban-GEE is a collection of scripts designed to analyze urbanization patterns using Google Earth Engine (GEE) and various data processing tools. This repository includes JavaScript and Python scripts for data aggregation, visualization, and analysis.

## Repository Structure

The repository contains the following key files and directories:

- `Archive/`: Directory containing datasets used in the analyses. Also contains code for merging population files(`merger.py`) and producing maps for Der Salam(`gee_sample_maps`) and world regions(`regions`).

- `Double bin population.js`: JavaScript script for GEE to perform double binning for two years on population data.

- `Urbanization.js`: JavaScript script for aggregating urbanization data using GEE.

- `UrbanizationV2.js`: An updated version of the `Urbanization.js` with the second definition of urbanization used.

- `environment.yml`: Configuration file for setting up the Python environment with necessary dependencies.

- `fullagg.js`: JavaScript script for performing full aggregation of spatial data in GEE. Needs fix

- `gee_sample_maps.py`: Python script to generate sample maps from GEE data.

- `heatmaps.py`: Python script for creating heatmaps for population density combinations for 1980 & 2020 and 2000 & 2020.

- `lag_bin.js`: JavaScript script implementing lag binning techniques in GEE.

- `mergeSSA.py`: Python script to merge datasets specific to Sub-Saharan Africa.

- `merger.py`: General-purpose Python script for merging multiple datasets.

- `scatter_plots.py`: Python script containing functions to generate scatter plots for urban change variables.

- `population_proportion.py`: Python script to calculate population proportions from datasets.

- `regionagg.js`: JavaScript script for regional aggregation of data in GEE.

- `regions.py`: Python script defining and handling different regional datasets.

- `replication_plots2.py`: Python script to replicate specific plots from studies or analyses.

- `reproduction_plots.py`: Python script for reproducing plots, possibly from external sources or publications.

- `tables.py`: Python script to generate tables summarizing data analyses.

## Getting Started

To set up the environment and run the scripts:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ssmunir/Urban-GEE.git
   cd Urban-GEE
2. **Run `Urbanization.js` and `UrbanizationV2.js` to produce urban population dataset.**
3. **Then `merger.py` to merge and aggregate data.**
4. **Run `replication_plots.py` to replicate figures fron `Henderson & Turner (2020)`**
