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

# group by country name and sum
data = data.groupby("country").sum().reset_index()


####### Generate summary statistics by region ##############

# Import income data 
incomeGroup = pd.read_csv(main_path + r"\Countries income group\income_class.csv")
incomeGroup = incomeGroup[["Economy", "Region", "Income group"]] # keep only relevant columns
incomeGroup = incomeGroup.rename(columns={"Economy": "country"})  # rename column to match main data column
popData = data.merge(incomeGroup, how="left", on="country") # merge income group with population data by country name 

# Drop countries with less than 100000 population in 2000
popData = popData.loc[popData['Population2000'] > 100000]

# Compute the final merged result and save it to a new CSV file
popData.to_csv(results + r"\full_population_data.csv")
print(f'Main population data saved at: {results}')

'''
# drop high income countries
lowMidIncome = popData[popData["Income group"] != "High income"]

##------------2010 - 2020---------------------------###
# main table 1  -- Region
t1regionCount = lowMidIncome[["Region", "Population2010"]].groupby('Region').agg(['count']).reset_index()
t1region = lowMidIncome[["Region", "Population2010", "Population2020", "UrbanPopulation2020", "UrbanPopulation2010", "UrbanPopulation_10YearLag2020"]].groupby('Region').agg(['sum']).reset_index()
t1region["popChange"] = t1region["Population2020"]["sum"] - t1region["Population2010"]["sum"]
t1region["urbanPopChange"] = t1region["UrbanPopulation2020"]["sum"] - t1region["UrbanPopulation2010"]["sum"]

maintableregion = pd.DataFrame()
maintableregion["Category"] = t1region["Region"]
maintableregion["Count"] = t1regionCount["Population2010"]["count"]
maintableregion["Population2010"] = t1region["Population2010"]["sum"]
maintableregion["popChangein2020"] = t1region["popChange"]
maintableregion["UrbanPopulation2010"] = t1region["UrbanPopulation2010"]["sum"]
maintableregion["urbanPopChange"] = t1region["urbanPopChange"]
maintableregion["UrbanPopulation_10YearLag2020"] = t1region["UrbanPopulation_10YearLag2020"]

# main table 1  -- Income group
t1IncomegroupCount = lowMidIncome[["Income group", "Population2010"]].groupby('Income group').agg(['count']).reset_index()
t1Incomegroup = lowMidIncome[["Income group", "Population2010", "Population2020", "UrbanPopulation2020", "UrbanPopulation2010", "UrbanPopulation_10YearLag2020"]].groupby("Income group").agg(["sum"]).reset_index()
t1Incomegroup["popChange"] = t1Incomegroup["Population2020"]["sum"] - t1Incomegroup["Population2010"]["sum"]
t1Incomegroup["urbanPopChange"] = t1Incomegroup["UrbanPopulation2020"]["sum"] - t1Incomegroup["UrbanPopulation2010"]["sum"]

maintableIncomegroup = pd.DataFrame()
maintableIncomegroup["Category"] = t1Incomegroup["Income group"]
maintableIncomegroup["Count"] = t1IncomegroupCount["Population2010"]["count"]
maintableIncomegroup["Population2010"] = t1Incomegroup["Population2010"]["sum"]
maintableIncomegroup["popChangein2020"] = t1Incomegroup["popChange"]
maintableIncomegroup["UrbanPopulation2010"] = t1Incomegroup["UrbanPopulation2010"]["sum"]
maintableIncomegroup["urbanPopChange"] = t1Incomegroup["urbanPopChange"]
maintableIncomegroup["UrbanPopulation_10YearLag2020"] = t1Incomegroup["UrbanPopulation_10YearLag2020"]

### Append income group to regions
mainTable1 = maintableregion._append(maintableIncomegroup, ignore_index=True)
# save to csv
mainTable1.to_csv(results + r"\table1_2010and2020.csv")

##------------------2020 - 2030--------------------###
# main table 2  -- Region
t1regionCount = lowMidIncome[["Region", "Population2020"]].groupby('Region').agg(['count']).reset_index()
t1region = lowMidIncome[["Region", "Population2020", "Population2030", "UrbanPopulation2020", "UrbanPopulation2030", "UrbanPopulation_10YearLag2030"]].groupby('Region').agg(['sum']).reset_index()
t1region["popChange"] = t1region["Population2030"]["sum"] - t1region["Population2020"]["sum"]
t1region["urbanPopChange"] = t1region["UrbanPopulation2030"]["sum"] - t1region["UrbanPopulation2020"]["sum"]

maintableregion = pd.DataFrame()
maintableregion["Category"] = t1region["Region"]
maintableregion["Count"] = t1regionCount["Population2020"]["count"]
maintableregion["Population2020"] = t1region["Population2020"]["sum"]
maintableregion["popChangein2030"] = t1region["popChange"]
maintableregion["UrbanPopulation2020"] = t1region["UrbanPopulation2020"]["sum"]
maintableregion["urbanPopChange"] = t1region["urbanPopChange"]
maintableregion["UrbanPopulation_10YearLag2030"] = t1region["UrbanPopulation_10YearLag2030"]

# main table 2  -- Income group
t1IncomegroupCount = lowMidIncome[["Income group", "Population2020"]].groupby('Income group').agg(['count']).reset_index()
t1Incomegroup = lowMidIncome[["Income group", "Population2020", "Population2030", "UrbanPopulation2020", "UrbanPopulation2030", "UrbanPopulation_10YearLag2030"]].groupby("Income group").agg(["sum"]).reset_index()
t1Incomegroup["popChange"] = t1Incomegroup["Population2030"]["sum"] - t1Incomegroup["Population2020"]["sum"]
t1Incomegroup["urbanPopChange"] = t1Incomegroup["UrbanPopulation2030"]["sum"] - t1Incomegroup["UrbanPopulation2020"]["sum"]

maintableIncomegroup = pd.DataFrame()
maintableIncomegroup["Category"] = t1Incomegroup["Income group"]
maintableIncomegroup["Count"] = t1IncomegroupCount["Population2020"]["count"]
maintableIncomegroup["Population2020"] = t1Incomegroup["Population2020"]["sum"]
maintableIncomegroup["popChangein2030"] = t1Incomegroup["popChange"]
maintableIncomegroup["UrbanPopulation2020"] = t1Incomegroup["UrbanPopulation2020"]["sum"]
maintableIncomegroup["urbanPopChange"] = t1Incomegroup["urbanPopChange"]
maintableIncomegroup["UrbanPopulation_10YearLag2030"] = t1Incomegroup["UrbanPopulation_10YearLag2030"]

###Append income group to regions
mainTable2 = maintableregion._append(maintableIncomegroup, ignore_index=True)
# save to csv
mainTable2.to_csv(results + r"\table2_2020and2030.csv")


##------------------2000 - 2020--------------------###
# main table 3  -- Region
t1regionCount = lowMidIncome[["Region", "Population2000"]].groupby('Region').agg(['count']).reset_index()
t1region = lowMidIncome[["Region", "Population2000", "Population2020", "UrbanPopulation2000", "UrbanPopulation2020", "UrbanPopulation_20YearLag2020"]].groupby('Region').agg(['sum']).reset_index()
t1region["popChange"] = t1region["Population2020"]["sum"] - t1region["Population2000"]["sum"]
t1region["urbanPopChange"] = t1region["UrbanPopulation2020"]["sum"] - t1region["UrbanPopulation2000"]["sum"]

maintableregion = pd.DataFrame()
maintableregion["Category"] = t1region["Region"]
maintableregion["Count"] = t1regionCount["Population2000"]["count"]
maintableregion["Population2000"] = t1region["Population2000"]["sum"]
maintableregion["popChangein2020"] = t1region["popChange"]
maintableregion["UrbanPopulation2000"] = t1region["UrbanPopulation2000"]["sum"]
maintableregion["urbanPopChange"] = t1region["urbanPopChange"]
maintableregion["UrbanPopulation_20YearLag2020"] = t1region["UrbanPopulation_20YearLag2020"]

# main table 3  -- Income group
t1IncomegroupCount = lowMidIncome[["Income group", "Population2000"]].groupby('Income group').agg(['count']).reset_index()
t1Incomegroup = lowMidIncome[["Income group", "Population2000", "Population2020", "UrbanPopulation2000", "UrbanPopulation2020", "UrbanPopulation_20YearLag2020"]].groupby("Income group").agg(["sum"]).reset_index()
t1Incomegroup["popChange"] = t1Incomegroup["Population2020"]["sum"] - t1Incomegroup["Population2000"]["sum"]
t1Incomegroup["urbanPopChange"] = t1Incomegroup["UrbanPopulation2020"]["sum"] - t1Incomegroup["UrbanPopulation2000"]["sum"]

maintableIncomegroup = pd.DataFrame()
maintableIncomegroup["Category"] = t1Incomegroup["Income group"]
maintableIncomegroup["Count"] = t1IncomegroupCount["Population2000"]["count"]
maintableIncomegroup["Population2000"] = t1Incomegroup["Population2000"]["sum"]
maintableIncomegroup["popChangein2020"] = t1Incomegroup["popChange"]
maintableIncomegroup["UrbanPopulation2000"] = t1Incomegroup["UrbanPopulation2000"]["sum"]
maintableIncomegroup["urbanPopChange"] = t1Incomegroup["urbanPopChange"]
maintableIncomegroup["UrbanPopulation_20YearLag2020"] = t1Incomegroup["UrbanPopulation_20YearLag2020"]

### Append income group to regions
mainTable2 = maintableregion._append(maintableIncomegroup, ignore_index=True)
# save to csv
mainTable2.to_csv(results + r"\table2_2000and2020.csv")

##------------------2010 - 2030--------------------###
# main table 3  -- Region
t1regionCount = lowMidIncome[["Region", "Population2010"]].groupby('Region').agg(['count']).reset_index()
t1region = lowMidIncome[["Region", "Population2010", "Population2030", "UrbanPopulation2010", "UrbanPopulation2030", "UrbanPopulation_20YearLag2030"]].groupby('Region').agg(['sum']).reset_index()
t1region["popChange"] = t1region["Population2030"]["sum"] - t1region["Population2010"]["sum"]
t1region["urbanPopChange"] = t1region["UrbanPopulation2030"]["sum"] - t1region["UrbanPopulation2010"]["sum"]

maintableregion = pd.DataFrame()
maintableregion["Category"] = t1region["Region"]
maintableregion["Count"] = t1regionCount["Population2010"]["count"]
maintableregion["Population2010"] = t1region["Population2010"]["sum"]
maintableregion["popChangein2030"] = t1region["popChange"]
maintableregion["UrbanPopulation2010"] = t1region["UrbanPopulation2010"]["sum"]
maintableregion["urbanPopChange"] = t1region["urbanPopChange"]
maintableregion["UrbanPopulation_20YearLag2030"] = t1region["UrbanPopulation_20YearLag2030"]

# main table 3  -- Income group
t1IncomegroupCount = lowMidIncome[["Income group", "Population2010"]].groupby('Income group').agg(['count']).reset_index()
t1Incomegroup = lowMidIncome[["Income group", "Population2010", "Population2030", "UrbanPopulation2010", "UrbanPopulation2030", "UrbanPopulation_20YearLag2030"]].groupby("Income group").agg(["sum"]).reset_index()
t1Incomegroup["popChange"] = t1Incomegroup["Population2030"]["sum"] - t1Incomegroup["Population2010"]["sum"]
t1Incomegroup["urbanPopChange"] = t1Incomegroup["UrbanPopulation2030"]["sum"] - t1Incomegroup["UrbanPopulation2010"]["sum"]

maintableIncomegroup = pd.DataFrame()
maintableIncomegroup["Category"] = t1Incomegroup["Income group"]
maintableIncomegroup["Count"] = t1IncomegroupCount["Population2010"]["count"]
maintableIncomegroup["Population2010"] = t1Incomegroup["Population2010"]["sum"]
maintableIncomegroup["popChangein2030"] = t1Incomegroup["popChange"]
maintableIncomegroup["UrbanPopulation2010"] = t1Incomegroup["UrbanPopulation2010"]["sum"]
maintableIncomegroup["urbanPopChange"] = t1Incomegroup["urbanPopChange"]
maintableIncomegroup["UrbanPopulation_20YearLag2030"] = t1Incomegroup["UrbanPopulation_20YearLag2030"]

### Append income group to regions
mainTable2 = maintableregion._append(maintableIncomegroup, ignore_index=True)
# save to csv
mainTable2.to_csv(results + r"\table2_2010and2030.csv")
print(f'All results saved at: {results}')
'''


