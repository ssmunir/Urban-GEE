import os
import dask.dataframe as dd
import pandas as pd
import pycountry_convert as pc 

# Define the folder containing the CSV files
main_path = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE"  # main folder containing all data
pop_def1 = main_path + r"\_archive\Population data def1"  # urban class 1 data folder
results1 = main_path + r"\data\gen"   # urban class 1 result folder


# --------------- urban definition 1 ------------------------------


# Loop through all files in the folder and create a list of DataFrames
dataframes = []
for i, filename in enumerate(os.listdir(pop_def1)):
    if filename.endswith(".csv"):
        file_path = os.path.join(pop_def1, filename)

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

# rename population data country names to match Income class country name for better merge
data = country_renamer("Bahamas", "Bahamas, The")
data = country_renamer("Cape Verde", "Cabo Verde")
data = country_renamer("Czech Republic", "Czechia")
data = country_renamer("Congo, Dem. Rep.", "Democratic Republic of the Congo")
data = country_renamer("Congo, Rep.", "Republic of the Congo")
data = country_renamer(r"CÃ´te d'Ivoire", "Cote d'Ivoire")
data = country_renamer("Moldova", "Moldova, Republic of")

# group by country name and sum
data = data.groupby("country").sum().reset_index()


####### Generate summary statistics by region ##############

# Import income data 
incomeGroup = pd.read_csv(main_path + r"\_archive\income_class.csv")
incomeGroup = incomeGroup[["Economy", "Region", "Income group"]] # keep only relevant columns
incomeGroup = incomeGroup.rename(columns={"Economy": "country"})  # rename column to match main data column
popData = data.merge(incomeGroup, how="left", on="country") # merge income group with population data by country name 


# Compute the final merged result and save it to a new CSV file - 
popData.to_csv(results1 + r"\urbanchange_summary_stats1.csv")
print(f'Main population data saved at: {results1}')


# -------------------------------------- urban definition 2 ------------------------------

pop_def2 = main_path + r"\_archive\Population data def2"  # urban class 1 data folder
results2 = main_path + r"\data\gen"   # urban class 1 result folder

# Loop through all files in the folder and create a list of DataFrames
dataframes = []
for i, filename in enumerate(os.listdir(pop_def2)):
    if filename.endswith(".csv"):
        file_path = os.path.join(pop_def2, filename)

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

# rename population data country names to match Income class country name for better merge
data = country_renamer("Bahamas", "Bahamas, The")
data = country_renamer("Cape Verde", "Cabo Verde")
data = country_renamer("Czech Republic", "Czechia")
data = country_renamer("Congo, Dem. Rep.", "Democratic Republic of the Congo")
data = country_renamer("Congo, Rep.", "Republic of the Congo")
data = country_renamer("CÃ´te d'Ivoire", "Cote d'Ivoire")
data = country_renamer("Moldova", "Moldova, Republic of")

# group by country name and sum
data = data.groupby("country").sum().reset_index()


####### Generate summary statistics by region ##############

# Import income data 
incomeGroup = pd.read_csv(main_path + r"\_archive\income_class.csv")
incomeGroup = incomeGroup[["Economy", "Region", "Income group"]] # keep only relevant columns
incomeGroup = incomeGroup.rename(columns={"Economy": "country"})  # rename column to match main data column
popData = data.merge(incomeGroup, how="left", on="country") # merge income group with population data by country name 


# Compute the final merged result and save it to a new CSV file
popData.to_csv(results2 + r"\urbanchange_summary_stats2.csv")
print(f'Main population data saved at: {results2}')

