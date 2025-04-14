import pandas as pd
from tabulate import tabulate
import numpy as np
import os

def generate_urban_tables(data1_path, data2_path, output_dir=None):
    """
    Generate LaTeX tables for urban population data by income groups and regions.
    
    Parameters:
    -----------
    data1_path : str
        Path to the SMOD definition 1 dataset
    data2_path : str
        Path to the SMOD definition 2 dataset
    output_dir : str, optional
        Directory where output files should be saved
    
    Returns:
    --------
    tuple
        (income_latex, region_latex) - LaTeX code for both tables
    """
    # Set output directory if provided
    if output_dir is not None:
        os.chdir(output_dir)
    
    # Load the data
    df = pd.read_csv(data1_path)
    df2 = pd.read_csv(data2_path)
    
    # Create copies for different groupings
    income_df1 = df.copy()
    income_df2 = df2.copy()
    region_df1 = df.copy()
    region_df2 = df2.copy()
    
    # Define mapping dictionaries
    income_group_mapping = {
        "High income": "HICs",
        "Low income": "LICs",
        "Lower middle income": "LMICs",
        "Upper middle income": "UMICs"
    }
    
    region_group_mapping = {
        "Sub-Saharan Africa": "SSA",
        "North America": "NA",
        "Middle East & North Africa": "MENA",
        "South Asia": "SA",
        "Latin America & Caribbean": "LAC",
        "East Asia & Pacific": "EAP",
        "Europe & Central Asia": "ECA"
    }
    
    # Apply mappings
    income_df1["Income group"] = income_df1["Income group"].replace(income_group_mapping)
    income_df2["Income group"] = income_df2["Income group"].replace(income_group_mapping)
    region_df1["Region"] = region_df1["Region"].replace(region_group_mapping)
    region_df2["Region"] = region_df2["Region"].replace(region_group_mapping)
    
    # Function to format population values
    def format_population(value):
        """Format population values in billions"""
        if pd.isna(value):
            return "N/A"
        else:
            return f"{value/1_000_000_000:.2f}".replace('.00', '')
        
        # Function to format population change values
        def format_population_change(value):
            """Format population values in millions"""
            if pd.isna(value):
                return "N/A"
            else:
                return f"{int(value/1_000_000)}"
    
    # Function to format percentage values
    def format_percent(value):
        """Format percentage values with proper handling of NaN values"""
        if pd.isna(value):
            return "N/A"
        val = float(value)
        return f"{round(val, 2)}"
    
    # Function to process data for either grouping
    def process_urban_data(df1, df2, group_col):
        # Process SMOD definition 1
        smod1 = df1.groupby(group_col).agg({
            'UrbanPopulation2010': 'sum',
            'UrbanPopulation2020': 'sum',
            'c3UrbanPopChange_2010-2020': 'sum',
            'c2UrbanPopChange_2010-2020': 'sum',
            'UrbanLand2020': 'sum',
            'TotalLandArea': 'sum',
            'urban2020not2010': 'sum'
        })
        
        # Calculate new columns
        smod1["urbanPopChange2010_2020"] = smod1["UrbanPopulation2020"] - smod1["UrbanPopulation2010"]
        smod1["Urban2020"] = smod1['UrbanPopulation2010'] + smod1['urbanPopChange2010_2020']
        smod1['urbanpopchange'] = smod1['c3UrbanPopChange_2010-2020'] + smod1['c2UrbanPopChange_2010-2020']
        smod1['shareUrban2020'] = (smod1['UrbanLand2020']/smod1['TotalLandArea'])*100
        smod1['shUrban2020not2010'] = (smod1['urban2020not2010']/smod1['UrbanLand2020'])*100
        # Handle potential division by zero
        smod1['perchange'] = smod1.apply(
            lambda x: (x["c2UrbanPopChange_2010-2020"]/x["urbanpopchange"])*100 
            if x["urbanpopchange"] != 0 else 0, 
            axis=1
        )
        
        # Select only the columns needed for the final output
        smod1 = smod1[["Urban2020", 'urbanpopchange', 'perchange', 'shareUrban2020', 'shUrban2020not2010' ]]
        
        # Process SMOD definition 2
        smod2 = df2.groupby(group_col).agg({
            'UrbanPopulation2010': 'sum',
            'UrbanPopulation2020': 'sum',
            'c3UrbanPopChange_2010-2020': 'sum',
            'c2UrbanPopChange_2010-2020': 'sum',
            'UrbanLand2020': 'sum',
            'TotalLandArea': 'sum',
            'urban2020not2010': 'sum'
        })
        
        # Calculate new columns
        smod2["urbanPopChange2010_2020"] = smod2["UrbanPopulation2020"] - smod2["UrbanPopulation2010"]
        smod2["Urban2020"] = smod2['UrbanPopulation2010'] + smod2['urbanPopChange2010_2020']
        smod2['urbanpopchange'] = smod2['c3UrbanPopChange_2010-2020'] + smod2['c2UrbanPopChange_2010-2020']
        smod2['shareUrban2020'] = (smod2['UrbanLand2020']/smod2['TotalLandArea'])*100
        smod2['shUrban2020not2010'] = (smod2['urban2020not2010']/smod2['UrbanLand2020'])*100
        # Handle potential division by zero
        smod2['perchange'] = smod2.apply(
            lambda x: (x["c2UrbanPopChange_2010-2020"]/(x["c2UrbanPopChange_2010-2020"] + x["c3UrbanPopChange_2010-2020"]))*100 
            if (x["c2UrbanPopChange_2010-2020"] + x["c3UrbanPopChange_2010-2020"]) != 0 else 0, 
            axis=1
        )
        
        # Select only the columns needed for the final output
        smod2 = smod2[["Urban2020", 'urbanpopchange', 'perchange', 'shareUrban2020', 'shUrban2020not2010']]
        
        return smod1, smod2
    
    # Process data for both groupings
    income_smod1, income_smod2 = process_urban_data(income_df1, income_df2, "Income group")
    region_smod1, region_smod2 = process_urban_data(region_df1, region_df2, "Region")
    
    # Format income data
    income_smod1_formatted = income_smod1.copy()
    income_smod2_formatted = income_smod2.copy()
    
    for df in [income_smod1_formatted, income_smod2_formatted]:
        df['Urban2020'] = df['Urban2020'].apply(format_population)
        df['urbanpopchange'] = df['urbanpopchange'].apply(format_population)
        df['perchange'] = df['perchange'].apply(format_percent)
        df['shareUrban2020'] = df['shareUrban2020'].apply(format_percent)
        df['shUrban2020not2010'] = df['shUrban2020not2010'].apply(format_percent)
    
    # Format region data
    region_smod1_formatted = region_smod1.copy()
    region_smod2_formatted = region_smod2.copy()
    
    for df in [region_smod1_formatted, region_smod2_formatted]:
        df['Urban2020'] = df['Urban2020'].apply(format_population)
        df['urbanpopchange'] = df['urbanpopchange'].apply(format_population)
        df['perchange'] = df['perchange'].apply(format_percent)
        df['shareUrban2020'] = df['shareUrban2020'].apply(format_percent)
        df['shUrban2020not2010'] = df['shUrban2020not2010'].apply(format_percent)
    
    
    # Generate LaTeX table for income groups
    income_groups = ["HICs", "UMICs", "LMICs", "LICs"]
    income_latex_table = r"""
\begin{tabular}{lcccc}
\hline\hline
         & HICs & UMICs & LMICs & LICs \\
\hline
         \multicolumn{5}{c}{\it Restrict to land that is urban in 2020 based on SMOD definition 1}\\
\hline
     Urban \% of all land in 2020  & """ + income_smod1_formatted.loc['HICs', 'shareUrban2020'] + r""" & """ + income_smod1_formatted.loc['UMICs', 'shareUrban2020'] + r""" & """ + income_smod1_formatted.loc['LMICs', 'shareUrban2020'] + r""" & """ + income_smod1_formatted.loc['LICs', 'shareUrban2020'] + r""" \\
    Turned urban since 2010  \% of 2020 urban land & """ + income_smod1_formatted.loc['HICs', 'shUrban2020not2010'] + r""" & """ + income_smod1_formatted.loc['UMICs', 'shUrban2020not2010'] + r""" & """ + income_smod1_formatted.loc['LMICs', 'shUrban2020not2010'] + r""" & """ + income_smod1_formatted.loc['LICs', 'shUrban2020not2010'] + r""" \\
     Population in 2020 on 2020 urban land (billions)         & """ + income_smod1_formatted.loc['HICs', 'Urban2020'] + r""" & """ + income_smod1_formatted.loc['UMICs', 'Urban2020'] + r""" & """ + income_smod1_formatted.loc['LMICs', 'Urban2020'] + r""" & """ + income_smod1_formatted.loc['LICs', 'Urban2020'] + r""" \\
     $\Delta$ pop. since 2010 on 2020 urban land (millions) & """ + income_smod1_formatted.loc['HICs', 'urbanpopchange'] + r"""   & """ + income_smod1_formatted.loc['UMICs', 'urbanpopchange'] + r"""  & """ + income_smod1_formatted.loc['LMICs', 'urbanpopchange'] + r"""  & """ + income_smod1_formatted.loc['LICs', 'urbanpopchange'] + r""" \\
     \% of $\Delta$ on land turned urban since 2010 & """ + income_smod1_formatted.loc['HICs', 'perchange'] + r""" & """ + income_smod1_formatted.loc['UMICs', 'perchange'] + r""" & """ + income_smod1_formatted.loc['LMICs', 'perchange'] + r""" & """ + income_smod1_formatted.loc['LICs', 'perchange'] + r""" \\
    \hline
         \multicolumn{5}{c}{\it Restrict to land that is urban in 2020 based on SMOD definition 2}\\
\hline
    Urban \% of all land in 2020  & """ + income_smod2_formatted.loc['HICs', 'shareUrban2020'] + r""" & """ + income_smod2_formatted.loc['UMICs', 'shareUrban2020'] + r""" & """ + income_smod2_formatted.loc['LMICs', 'shareUrban2020'] + r""" & """ + income_smod2_formatted.loc['LICs', 'shareUrban2020'] + r""" \\
    Turned urban since 2010  \% of 2020 urban land & """ + income_smod2_formatted.loc['HICs', 'shUrban2020not2010'] + r""" & """ + income_smod2_formatted.loc['UMICs', 'shUrban2020not2010'] + r""" & """ + income_smod2_formatted.loc['LMICs', 'shUrban2020not2010'] + r""" & """ + income_smod2_formatted.loc['LICs', 'shUrban2020not2010'] + r""" \\
     Population in 2020 on 2020 urban land (billions)         & """ + income_smod2_formatted.loc['HICs', 'Urban2020'] + r""" & """ + income_smod2_formatted.loc['UMICs', 'Urban2020'] + r""" & """ + income_smod2_formatted.loc['LMICs', 'Urban2020'] + r""" & """ + income_smod2_formatted.loc['LICs', 'Urban2020'] + r""" \\
     $\Delta$ pop. since 2010 on 2020 urban land (millions) & """ + income_smod2_formatted.loc['HICs', 'urbanpopchange'] + r"""   & """ + income_smod2_formatted.loc['UMICs', 'urbanpopchange'] + r"""  & """ + income_smod2_formatted.loc['LMICs', 'urbanpopchange'] + r"""  & """ + income_smod2_formatted.loc['LICs', 'urbanpopchange'] + r""" \\
     \% of $\Delta$ on land turned urban since 2010 & """ + income_smod2_formatted.loc['HICs', 'perchange'] + r""" & """ + income_smod2_formatted.loc['UMICs', 'perchange'] + r""" & """ + income_smod2_formatted.loc['LMICs', 'perchange'] + r""" & """ + income_smod2_formatted.loc['LICs', 'perchange'] + r"""\\
         \hline\hline
\end{tabular}
"""
    
    # Generate LaTeX table for regions dynamically
    regions = ["SSA", "NA", "MENA", "SA", "LAC", "EAP", "ECA"]
    region_headers = " & ".join(regions)
    
   # Updated region latex table generation
    region_latex_table = r"""
    \resizebox{\textwidth}{!}{%
\begin{tabular}{l""" + "c" * len(regions) + r"""}
\hline\hline
         & """ + region_headers + r""" \\
\hline
         \multicolumn{""" + str(len(regions) + 1) + r"""}{c}{\it Restrict to land that is urban in 2020 based on SMOD definition 1}\\
\hline
     Urban \% of all land in 2020         & """
    # Add share of urban land values for all regions (SMOD definition 1)
    urban_land_share_values = []
    for region in regions:
        if region in region_smod1_formatted.index:
            urban_land_share_values.append(region_smod1_formatted.loc[region, 'shareUrban2020'])
        else:
            urban_land_share_values.append("N/A")
    region_latex_table += r""" & """.join(urban_land_share_values) + r""" \\
     Turned urban since 2010  \% of 2020 urban land& """
    
    # Add share of land turned urban values for all regions (SMOD definition 1)
    land_turned_urban_values = []
    for region in regions:
        if region in region_smod1_formatted.index:
            land_turned_urban_values.append(region_smod1_formatted.loc[region, 'shUrban2020not2010'])
        else:
            land_turned_urban_values.append("N/A")
    region_latex_table += r""" & """.join(land_turned_urban_values) + r""" \\
        Population in 2020 on 2020 urban land (billions)         & """
    # Add population values for all regions
    pop_values = []
    for region in regions:
        if region in region_smod1_formatted.index:
            pop_values.append(region_smod1_formatted.loc[region, 'Urban2020'])
        else:
            pop_values.append("N/A")
    region_latex_table += r""" & """.join(pop_values) + r""" \\
     $\Delta$ pop. since 2010 on 2020 urban land (millions) & """
    
    # Add change values for all regions
    change_values = []
    for region in regions:
        if region in region_smod1_formatted.index:
            change_values.append(region_smod1_formatted.loc[region, 'urbanpopchange'])
        else:
            change_values.append("N/A")
    region_latex_table += r""" & """.join(change_values) + r""" \\
     \% of $\Delta$ on land turned urban since 2010 & """
    
    # Add percentage values for all regions
    pct_values = []
    for region in regions:
        if region in region_smod1_formatted.index:
            pct_values.append(region_smod1_formatted.loc[region, 'perchange'])
        else:
            pct_values.append("N/A")
    region_latex_table += r""" & """.join(pct_values) + r""" \\
\hline
         \multicolumn{""" + str(len(regions) + 1) + r"""}{c}{\it Restrict to land that is urban in 2020 based on SMOD definition 2}\\
\hline
     Urban \% of all land in 2020        & """
    
    # Add share of urban land values for all regions (SMOD definition 2)
    urban_land_share_values2 = []
    for region in regions:
        if region in region_smod2_formatted.index:
            urban_land_share_values2.append(region_smod2_formatted.loc[region, 'shareUrban2020'])
        else:
            urban_land_share_values2.append("N/A")
    region_latex_table += r""" & """.join(urban_land_share_values2) + r""" \\
     Turned urban since 2010  \% of 2020 urban land & """
    
    # Add share of land turned urban values for all regions (SMOD definition 2)
    land_turned_urban_values2 = []
    for region in regions:
        if region in region_smod2_formatted.index:
            land_turned_urban_values2.append(region_smod2_formatted.loc[region, 'shUrban2020not2010'])
        else:
            land_turned_urban_values2.append("N/A")
    region_latex_table += r""" & """.join(land_turned_urban_values2) + r""" \\
     Population in 2020 on 2020 urban land (billions)         & """
    
    # Repeat similar logic for SMOD definition 2
    # Add population values for all regions (definition 2)
    pop_values2 = []
    for region in regions:
        if region in region_smod2_formatted.index:
            pop_values2.append(region_smod2_formatted.loc[region, 'Urban2020'])
        else:
            pop_values2.append("N/A")
    region_latex_table += r""" & """.join(pop_values2) + r""" \\
     $\Delta$ pop. since 2010 on 2020 urban land (millions) & """
    
    # Add change values for all regions (definition 2)
    change_values2 = []
    for region in regions:
        if region in region_smod2_formatted.index:
            change_values2.append(region_smod2_formatted.loc[region, 'urbanpopchange'])
        else:
            change_values2.append("N/A")
    region_latex_table += r""" & """.join(change_values2) + r""" \\
     \% of $\Delta$ on land turned urban since 2010 & """
    
    # Add percentage values for all regions (definition 2)
    pct_values2 = []
    for region in regions:
        if region in region_smod2_formatted.index:
            pct_values2.append(region_smod2_formatted.loc[region, 'perchange'])
        else:
            pct_values2.append("N/A")
    region_latex_table += r""" & """.join(pct_values2) + r""" \\
\hline\hline
\end{tabular}%
}
"""
    """
    
    # Define the full names for regions
    region_full_names = {
        "SSA": "Sub-Saharan Africa",
        "NA": "North America",
        "MENA": "Middle East and North Africa", 
        "SA": "South Asia",
        "LAC": "Latin America and Caribbean",
        "EAP": "East Asia and Pacific",
        "ECA": "Europe and Central Asia"
    }
    
    # Define the full names for income groups
    income_full_names = {
        "HICs": "High-income Countries",
        "UMICs": "Upper Middle-income Countries",
        "LMICs": "Lower Middle-income Countries",
        "LICs": "Low-income Countries"
    }
    
    # Create the note for region names
    region_notes = "Notes: "
    for abbr, full_name in region_full_names.items():
        region_notes += f"{abbr} = {full_name}; "
    region_notes = region_notes.rstrip("; ") + "."
    
    # Create the note for income groups
    income_notes = "Notes: "
    for abbr, full_name in income_full_names.items():
        income_notes += f"{abbr} = {full_name}; "
    income_notes = income_notes.rstrip("; ") + "."
    
    # FIX: Create notes without including the tables again
    region_notes_latex = r"\vspace{0.5em}" + "\n" + r"\begin{flushleft}" + "\n" + r"\footnotesize " + region_notes + "\n" + r"\end{flushleft}"
    income_notes_latex = r"\vspace{0.5em}" + "\n" + r"\begin{flushleft}" + "\n" + r"\footnotesize " + income_notes + "\n" + r"\end{flushleft}"
    """
    # FIX: Just append the notes after the tables
    final_region_latex = region_latex_table
    final_income_latex = income_latex_table 
    
    # Save tables to files
    with open('urban_population_by_income.tex', 'w') as f:
        f.write(final_income_latex)
    
    with open('urban_population_by_region.tex', 'w') as f:
        f.write(final_region_latex)
    
    print("LaTeX tables saved to 'urban_population_by_income.tex' and 'urban_population_by_region.tex'")
    
    return final_income_latex, final_region_latex

# Example usage
if __name__ == "__main__":
    
    if os.getlogin() == "tanner_regan":
        main_path=r"C:\Users\tanner_regan\Documents\GitHub\Urban-GEE/" 
    elif os.getlogin() == "auuser":
        main_path = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE/"
    else: raise ValueError('Path not correctly specified for this computer.')

    data1 = main_path + r"\data\gen\urbanchange_summary_stats1.csv"
    data2 = main_path + r"\data\gen\urbanchange_summary_stats2.csv"
    output_dir = main_path + r"\tables"
    
    income_table, region_table = generate_urban_tables(data1, data2, output_dir)
    
    print(f"Tables are saved to {output_dir}")