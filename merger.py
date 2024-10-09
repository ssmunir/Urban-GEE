#pip install dask[dataframe]

import os
import dask.dataframe as dd
import pandas as pd
import pycountry_convert as pc 

# Define the folder containing the CSV files
main_path = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\Data"
folder_path = main_path + r"\Population data"
results = main_path + r"\Results"

# Loop through all files in the folder and create a list of DataFrames
dataframes = []
for i, filename in enumerate(os.listdir(folder_path)):
    if filename.endswith(".csv"):
        file_path = os.path.join(folder_path, filename)

        # Read the CSV using Dask
        df = dd.read_csv(file_path)

        # Round all population columns to whole numbers (if not the 'country' column)
        for col in df.columns:
            if col != "country":
                df[col] = df[col].round(0).astype("Int64")  # Round nd convert to integer
        
        # If not the first file, drop the 'country' column.
        if i != 0:
            df = df.drop(columns=["country"])

        dataframes.append(df)

# Concatenate all DataFrames
merged_df = dd.concat(dataframes, axis=1)

# Merge rows with the same country name and sum their values.
merged_df = merged_df.groupby("country").sum().reset_index()

# create population pandas datafram
data = merged_df.compute()

# create function to rename country with pycountry_convert recognized country name
def country_renamer(data_name, real_name):
    data_n = data.replace(data_name, real_name)
    return data_n

# rename country names to match names recognized by pycountry_convert for easy continent identification
data = country_renamer("U.K. of Great Britain and Northern Ireland", "Great Britain")
data = country_renamer("China/India", "China")
data = country_renamer("Iran  (Islamic Republic of)", "Iran, Islamic Republic of")
data = country_renamer("Micronesia (Federated States of)", "Micronesia, Federated States of")
data = country_renamer("Turks and Caicos islands", "Turks and Caicos Islands")
data = country_renamer("Timor-Leste", "Timor-Leste")
data = country_renamer("Republic of Korea", "Korea, Republic Of")
data = country_renamer("Saint Pierre et Miquelon", "Saint Pierre and Miquelon")
data = country_renamer("Svalbard and Jan Mayen Islands", "Svalbard and Jan Mayen")
data = country_renamer("Saint Helena", "Saint Helena, Ascension and Tristan da Cunha")
data = country_renamer("Dem People's Rep of Korea", "Democratic People's Republic of Korea")
data = country_renamer("The former Yugoslav Republic of Macedonia", "Macedonia, The Former Yugoslav Republic Of")


# define function to add continent name 
def country_to_continent(country_name):
    try:
        country_alpha2 = pc.country_name_to_country_alpha2(country_name)
        country_continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
        country_continent_name = pc.convert_continent_code_to_continent_name(country_continent_code)
        return country_continent_name
    except KeyError as e:
        return None
 
# insert continent column beside the country column
country_name = data["country"]  # list with country names 
continent_name = [country_to_continent(i) for i in country_name] # list with continent names
data.insert(1, "continent", continent_name)  # insert column 

# group by country name and sum
data = data.groupby("country").sum().reset_index()



# rename population data country names to match Income class country name for better merge
data = country_renamer("Taiwan", "Taiwan, China")
data = country_renamer("Turkey", "Türkiye")
data = country_renamer("United Republic of Tanzania", "Tanzania")
data = country_renamer("Iran, Islamic Republic of", "Iran, Islamic Rep.")
data = country_renamer("Democratic People's Republic of Korea", "Korea, Dem. People's Rep.")
data = country_renamer("Viet Nam", "Vietnam")
data = country_renamer("United States Virgin Islands", "Virgin Islands (U.S.)")
data = country_renamer("Yemen", "Yemen, Rep.")
data = country_renamer("West Bank", "West Bank and Gaza")
data = country_renamer("Venezuela", "Venezuela, RB")
data = country_renamer("United States of America", "United States")
data = country_renamer("Korea, Republic Of", "Korea, Rep.")
data = country_renamer("Great Britain", "United Kingdom")
data = country_renamer("Saint Vincent and the Grenadines", "St. Vincent and the Grenadines")
data = country_renamer("Saint Lucia", "St Lucia")
data = country_renamer("Saint Kitts and Nevis", "St. Kitts and Nevis")
data = country_renamer("Democratic Republic of the Congo", "Congo, Dem. Rep.")
data = country_renamer("Egypt", "Egypt, Arab Rep.")
data = country_renamer("Gambia", "Gambia, The")
data = country_renamer("Hong Kong", "Hong Kong SAR, China")
data = country_renamer("Lao People's Democratic Republic", "Lao PDR")
data = country_renamer("Macau", "Macao SAR, China")
data = country_renamer("Micronesia, Federated States of", "Micronesia, Fed. Sts.")
data = country_renamer("Moldova, Republic of", "Moldova")
data = country_renamer("Sao Tome and Principe", "São Tomé and Príncipe")


# Compute the final merged result and save it to a new CSV file
output_path = os.path.join(results, r"full_population_data.csv")
data.to_csv(output_path)
print(f'Main population data saved at: {output_path}')


####### Generate summary statistics by region ##############

# Import income data 
incomeGroup = pd.read_csv(r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\Data\Counties income group\income_class.csv")
incomeGroup = incomeGroup[["Economy", "Region", "Income group"]] # keep only relevant columns
incomeGroup = incomeGroup.rename(columns={"Economy": "country"})  # rename column to match main data column
popData = data.merge(incomeGroup, how="left", on="country") # merge income group with population data by country name 

# drop high income countries
lowMidIncome = popData[popData["Income group"] != "High income"]
"""
lowIncome = lowIncome[['Population2000', 'Population2010',
       'Population2020', 'Population2030', 'UrbanPopulation_10YearLag2000',
       'UrbanPopulation_10YearLag2010', 'UrbanPopulation_10YearLag2020',
       'UrbanPopulation_10YearLag2030', 'UrbanPopulation_20YearLag2000',
       'UrbanPopulation_20YearLag2010', 'UrbanPopulation_20YearLag2020',
       'UrbanPopulation_20YearLag2030', 'UrbanPopulation2000',
       'UrbanPopulation2010', 'UrbanPopulation2020', 'UrbanPopulation2030', 'Region']]
"""



lowMidIncome2010 = lowMidIncome[['Region', 'Population2010','UrbanPopulation2010',
                           'UrbanPopulation_10YearLag2010','UrbanPopulation_20YearLag2010']] # group 2010 data

lowMidIncome2020 = lowMidIncome[['Region','Population2020','UrbanPopulation2020',
                            'UrbanPopulation_10YearLag2020','UrbanPopulation_20YearLag2020']] # group 2020 data
# Summary stats by region for 2010 and 2020
lowMidIncomeByRegion2010 = lowMidIncome2010.groupby('Region').agg(['count', 'mean', 'min', 'max']).reset_index()
lowMidIncomeByRegion2020 = lowMidIncome2020.groupby('Region').agg(['count', 'mean', 'min', 'max']).reset_index()

# rename column to match
lowMidIncomeByRegion2010 = lowMidIncomeByRegion2010.rename(columns={"Region": "category"})
lowMidIncomeByRegion2020 = lowMidIncomeByRegion2020.rename(columns={"Region": "category"})

#### Generate summary statistics by income group
lowMidIncome2010 = lowMidIncome[['Income group', 'Population2010','UrbanPopulation2010',
                           'UrbanPopulation_10YearLag2010','UrbanPopulation_20YearLag2010']] # group 2010 data 

lowMidIncome2020 = lowMidIncome[['Income group','Population2020','UrbanPopulation2020',
                            'UrbanPopulation_10YearLag2020','UrbanPopulation_20YearLag2020']] # group 2020 data

# Summary stats by income group for 2010 and 2020
lowMidIncomeByGroup2010 = lowMidIncome2010.groupby('Income group').agg(['count', 'mean', 'min', 'max']).reset_index()
lowMidIncomeByGroup2020 = lowMidIncome2020.groupby('Income group').agg(['count', 'mean', 'min', 'max']).reset_index()

# rename column to match
lowMidIncomeByGroup2010 = lowMidIncomeByGroup2010.rename(columns={"Income group": "category"})
lowMidIncomeByGroup2020 = lowMidIncomeByGroup2020.rename(columns={"Income group": "category"})

#### Append lowMidIncomeByRegion2010 and 2020 & lowMidIncomeByGroup2010 and 2020 to generate first table
table2010 = lowMidIncomeByRegion2010._append(lowMidIncomeByGroup2010, ignore_index=True)
table2020 = lowMidIncomeByRegion2020._append(lowMidIncomeByGroup2020, ignore_index=True)
# save summary statistics as csv 
table2010.to_csv(results + r"\summary_stats_2010.csv")
table2020.to_csv(results + r"\summary_stats_2020.csv")
print(f'Main population data saved at: {results}')





















