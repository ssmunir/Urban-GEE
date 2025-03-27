# Urban-GEE

Urban-GEE is a collection of scripts designed to analyze urbanization patterns using Google Earth Engine (GEE) and various data processing tools. This repository includes JavaScript and Python scripts for data aggregation, visualization, and analysis.

---

## Table of Contents
1. [Repository Structure](#repository-structure)
2. [Getting Started](#getting-started)
3. [Scripts Overview](#scripts-overview)
4. [Data and Outputs](#data-and-outputs)
5. [Contributing](#contributing)
6. [License](#license)

---

## Repository Structure

The repository contains the following key files and directories:

- `Archive/`: Directory containing datasets used in the analyses. Also contains code for merging population files (`merger.py`) and producing maps for Dar es Salaam (`gee_sample_maps.py`) and world regions (`regions.py`).

- `Double bin population.js`: JavaScript script for GEE to perform double binning for two years on population data.

- `Urbanization.js`: JavaScript script for aggregating urbanization data using GEE.

- `UrbanizationV2.js`: An updated version of the `Urbanization.js` with the second definition of urbanization used.

- `environment.yml`: Configuration file for setting up the Python environment with necessary dependencies.

- `fullagg.js`: JavaScript script for performing full aggregation of spatial data in GEE (needs fixes).

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

3. **Run the scripts in the following order:**
   - `Urbanization.js` and `UrbanizationV2.js` to produce urban population datasets.
   - `merger.py` to merge and aggregate data.
   - `replication_plots.py` to replicate figures from Henderson & Turner (2020).

---

## Scripts Overview

### JavaScript Scripts (GEE)
- **`Double bin population.js`**: Performs double binning for two years on population data.
- **`Urbanization.js`**: Aggregates urbanization data using GEE.
- **`UrbanizationV2.js`**: Updated version of `Urbanization.js` with a second definition of urbanization.
- **`fullagg.js`**: Performs full aggregation of spatial data in GEE (needs fixes).
- **`lag_bin.js`**: Implements lag binning techniques in GEE.
- **`regionagg.js`**: Performs regional aggregation of data in GEE.

### Python Scripts
- **`gee_sample_maps.py`**: Generates sample maps from GEE data.
- **`heatmaps.py`**: Creates heatmaps for population density combinations.
- **`merger.py`**: General-purpose script for merging multiple datasets.
- **`mergeSSA.py`**: Merges datasets specific to Sub-Saharan Africa.
- **`scatter_plots.py`**: Generates scatter plots for urban change variables.
- **`population_proportion.py`**: Calculates population proportions from datasets.
- **`regions.py`**: Defines and handles different regional datasets.
- **`replication_plots2.py`**: Replicates specific plots from studies or analyses.
- **`reproduction_plots.py`**: Reproduces plots, possibly from external sources.
- **`tables.py`**: Generates tables summarizing data analyses.

---

## Data and Outputs

- **Input Data**: Stored in the `Archive/` directory.
- **Generated Figures**: Saved in the `figures/` directory.
- **Summary Tables**: Stored in the `tables/` directory.

---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
