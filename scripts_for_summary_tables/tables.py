import os
import dask.dataframe as dd
import pandas as pd
import pycountry_convert as pc 

# Define the folder containing the CSV files
main_path = r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE"  # main folder containing all data
results1 = main_path + r"\tables\urbanchange_summary_stats1"   # urban class 1 result folder
results2 = main_path + r"\tables\urbanchange_summary_stats2"   # urban class 2 result folder

# ------------------------------------ Tables generated from 1 population data with urban >= 22 ---------------------------------#

popData = pd.read_csv(results1 + r"\full_population_data.csv")  # import pop data 1

# drop high income countries
lowMidIncome = popData[popData["Income group"] != "High income"]

##------------------------2010 - 2020---------------------------###
# main table 1  -- Region
t1regionCount = lowMidIncome[["Region", "Population2010"]].groupby('Region').agg(['count']).reset_index()
# Subset 2010 and 2020 
t1region = lowMidIncome[["Region", "Population2010","PopChange_2010-2020", "UrbanPopulation2010", "UrbanPopulation2020",  "UrbanPopulation_10YearLag2020", "NonUrbanPopulation_10YearLag2020"]].groupby('Region').agg(['sum']).reset_index()

maintableregion = pd.DataFrame()
maintableregion["Category"] = t1region["Region"]
maintableregion["Count"] = t1regionCount["Population2010"]["count"]
maintableregion["Population2010"] = t1region["Population2010"]["sum"]
maintableregion["popChangein2010_2020"] = t1region["PopChange_2010-2020"]["sum"]
maintableregion["UrbanPopulation2010"] = t1region["UrbanPopulation2010"]["sum"]
maintableregion["urbanPopChange2010_2020"] = t1region["UrbanPopulation2020"]["sum"] - t1region["UrbanPopulation2010"]["sum"]
maintableregion["UrbanPopulation_10YearLag2020"] = t1region["UrbanPopulation_10YearLag2020"]["sum"]
maintableregion["NonUrbanPopulation_10YearLag2020"] = t1region["NonUrbanPopulation_10YearLag2020"]["sum"]

# main table 1  -- Income group
t1IncomegroupCount = lowMidIncome[["Income group", "Population2010"]].groupby('Income group').agg(['count']).reset_index()
# Subset 2010 and 2020 
t1Incomegroup = lowMidIncome[["Income group", "Population2010","PopChange_2010-2020", "UrbanPopulation2010", "UrbanPopulation2020", "UrbanPopulation_10YearLag2020", "NonUrbanPopulation_10YearLag2020"]].groupby("Income group").agg(["sum"]).reset_index()

maintableIncomegroup = pd.DataFrame()
maintableIncomegroup["Category"] = t1Incomegroup["Income group"]
maintableIncomegroup["Count"] = t1IncomegroupCount["Population2010"]["count"]
maintableIncomegroup["Population2010"] = t1Incomegroup["Population2010"]["sum"]
maintableIncomegroup["popChangein2010_2020"] = t1Incomegroup["PopChange_2010-2020"]["sum"]
maintableIncomegroup["UrbanPopulation2010"] = t1Incomegroup["UrbanPopulation2010"]["sum"]
maintableIncomegroup["urbanPopChange2010_2020"] = t1Incomegroup["UrbanPopulation2020"]["sum"] - t1Incomegroup["UrbanPopulation2010"]["sum"]
maintableIncomegroup["UrbanPopulation_10YearLag2020"] = t1Incomegroup["UrbanPopulation_10YearLag2020"]["sum"]
maintableIncomegroup["NonUrbanPopulation_10YearLag2020"] = t1Incomegroup["NonUrbanPopulation_10YearLag2020"]["sum"]

### Append income group to regions
mainTable1 = maintableregion._append(maintableIncomegroup, ignore_index=True)
# save to csv
mainTable1.to_csv(results1 + r"\table1_2010and2020.csv")

##----------------------------- 2020 - 2030--------------------#### save to csv
# main table 2  -- Region
t1regionCount = lowMidIncome[["Region", "Population2020"]].groupby('Region').agg(['count']).reset_index()
# Subset 2020 and 2030 
t1region = lowMidIncome[["Region", "Population2020","PopChange_2020-2030", "UrbanPopulation2020", "UrbanPopulation2030", "UrbanPopulation_10YearLag2030", "NonUrbanPopulation_10YearLag2030"]].groupby('Region').agg(['sum']).reset_index()

maintableregion = pd.DataFrame()
maintableregion["Category"] = t1region["Region"]
maintableregion["Count"] = t1regionCount["Population2020"]["count"]
maintableregion["Population2020"] = t1region["Population2020"]["sum"]
maintableregion["popChangein2020_2030"] = t1region["PopChange_2020-2030"]["sum"]
maintableregion["UrbanPopulation2020"] = t1region["UrbanPopulation2020"]["sum"]
maintableregion["urbanPopChange2020_2030"] = t1region["UrbanPopulation2030"]["sum"] - t1region["UrbanPopulation2020"]["sum"]
maintableregion["UrbanPopulation_10YearLag2030"] = t1region["UrbanPopulation_10YearLag2030"]["sum"]
maintableregion["NonUrbanPopulation_10YearLag2030"] = t1region["NonUrbanPopulation_10YearLag2030"]["sum"]

# main table 2  -- Income group
t1IncomegroupCount = lowMidIncome[["Income group", "Population2020"]].groupby('Income group').agg(['count']).reset_index()
# Subset 2020 and 2030 
t1Incomegroup = lowMidIncome[["Income group", "Population2020","PopChange_2020-2030", "UrbanPopulation2020", "UrbanPopulation2030", "UrbanPopulation_10YearLag2030", "NonUrbanPopulation_10YearLag2030"]].groupby("Income group").agg(["sum"]).reset_index()

maintableIncomegroup = pd.DataFrame()
maintableIncomegroup["Category"] = t1Incomegroup["Income group"]
maintableIncomegroup["Count"] = t1IncomegroupCount["Population2020"]["count"]
maintableIncomegroup["Population2020"] = t1Incomegroup["Population2020"]["sum"]
maintableIncomegroup["popChangein2020_2030"] = t1Incomegroup["PopChange_2020-2030"]["sum"]
maintableIncomegroup["UrbanPopulation2020"] = t1Incomegroup["UrbanPopulation2020"]["sum"]
maintableIncomegroup["urbanPopChange2020_2030"] = t1Incomegroup["UrbanPopulation2030"]["sum"] - t1Incomegroup["UrbanPopulation2020"]["sum"]
maintableIncomegroup["UrbanPopulation_10YearLag2030"] = t1Incomegroup["UrbanPopulation_10YearLag2030"]["sum"]
maintableIncomegroup["NonUrbanPopulation_10YearLag2030"] = t1Incomegroup["NonUrbanPopulation_10YearLag2030"]["sum"]

### Append income group to regions
mainTable1 = maintableregion._append(maintableIncomegroup, ignore_index=True)
# save to csv
mainTable1.to_csv(results1 + r"\table1_2020and2030.csv")


##----------------------------- 2000 - 2020--------------------#### save to csv
# main table 3  -- Region
t1regionCount = lowMidIncome[["Region", "Population2000"]].groupby('Region').agg(['count']).reset_index()
# Subset 2000 and 2020 
t1region = lowMidIncome[["Region", "Population2000","PopChange_2000-2020", "UrbanPopulation2000", "UrbanPopulation2020", "UrbanPopulation_20YearLag2020", "NonUrbanPopulation_20YearLag2020"]].groupby('Region').agg(['sum']).reset_index()

maintableregion = pd.DataFrame()
maintableregion["Category"] = t1region["Region"]
maintableregion["Count"] = t1regionCount["Population2000"]["count"]
maintableregion["Population2000"] = t1region["Population2000"]["sum"]
maintableregion["popChangein2000_2020"] = t1region["PopChange_2000-2020"]["sum"]
maintableregion["UrbanPopulation2000"] = t1region["UrbanPopulation2000"]["sum"]
maintableregion["urbanPopChange2000_2020"] = t1region["UrbanPopulation2020"]["sum"] - t1region["UrbanPopulation2000"]["sum"]
maintableregion["UrbanPopulation_20YearLag2020"] = t1region["UrbanPopulation_20YearLag2020"]["sum"]
maintableregion["NonUrbanPopulation_20YearLag2020"] = t1region["NonUrbanPopulation_20YearLag2020"]["sum"]

# main table 3  -- Income group
t1IncomegroupCount = lowMidIncome[["Income group", "Population2000"]].groupby('Income group').agg(['count']).reset_index()
# Subset 2020 and 2030 
t1Incomegroup = lowMidIncome[["Income group", "Population2000","PopChange_2000-2020", "UrbanPopulation2000", "UrbanPopulation2020", "UrbanPopulation_20YearLag2020", "NonUrbanPopulation_20YearLag2020"]].groupby("Income group").agg(["sum"]).reset_index()

maintableIncomegroup = pd.DataFrame()
maintableIncomegroup["Category"] = t1Incomegroup["Income group"]
maintableIncomegroup["Count"] = t1IncomegroupCount["Population2000"]["count"]
maintableIncomegroup["Population2000"] = t1Incomegroup["Population2000"]["sum"]
maintableIncomegroup["popChangein2000_2020"] = t1Incomegroup["PopChange_2000-2020"]["sum"]
maintableIncomegroup["UrbanPopulation2000"] = t1Incomegroup["UrbanPopulation2000"]["sum"]
maintableIncomegroup["urbanPopChange2000_2020"] = t1Incomegroup["UrbanPopulation2020"]["sum"] - t1Incomegroup["UrbanPopulation2000"]["sum"]
maintableIncomegroup["UrbanPopulation_20YearLag2020"] = t1Incomegroup["UrbanPopulation_20YearLag2020"]["sum"]
maintableIncomegroup["NonUrbanPopulation_20YearLag2020"] = t1Incomegroup["NonUrbanPopulation_20YearLag2020"]["sum"]

### Append income group to regions
mainTable1 = maintableregion._append(maintableIncomegroup, ignore_index=True)
# save to csv
mainTable1.to_csv(results1 + r"\table1_2000and2020.csv")



##----------------------------- 2010 - 2030--------------------#### save to csv
# main table 4  -- Region
t1regionCount = lowMidIncome[["Region", "Population2010"]].groupby('Region').agg(['count']).reset_index()
# Subset 2010 and 2030 
t1region = lowMidIncome[["Region", "Population2010","PopChange_2010-2030", "UrbanPopulation2010", "UrbanPopulation2030", "UrbanPopulation_20YearLag2030", "NonUrbanPopulation_20YearLag2030"]].groupby('Region').agg(['sum']).reset_index()

maintableregion = pd.DataFrame()
maintableregion["Category"] = t1region["Region"]
maintableregion["Count"] = t1regionCount["Population2010"]["count"]
maintableregion["Population2010"] = t1region["Population2010"]["sum"]
maintableregion["popChangein2010_2030"] = t1region["PopChange_2010-2030"]["sum"]
maintableregion["UrbanPopulation2010"] = t1region["UrbanPopulation2010"]["sum"]
maintableregion["urbanPopChange2010_2030"] = t1region["UrbanPopulation2030"]["sum"] - t1region["UrbanPopulation2010"]["sum"]
maintableregion["UrbanPopulation_20YearLag2030"] = t1region["UrbanPopulation_20YearLag2030"]["sum"]
maintableregion["NonUrbanPopulation_20YearLag2030"] = t1region["NonUrbanPopulation_20YearLag2030"]["sum"]

# main table 4  -- Income group
t1IncomegroupCount = lowMidIncome[["Income group", "Population2010"]].groupby('Income group').agg(['count']).reset_index()
# Subset 2020 and 2030 
t1Incomegroup = lowMidIncome[["Income group", "Population2010","PopChange_2010-2030", "UrbanPopulation2010", "UrbanPopulation2030", "UrbanPopulation_20YearLag2030", "NonUrbanPopulation_20YearLag2030"]].groupby("Income group").agg(["sum"]).reset_index()

maintableIncomegroup = pd.DataFrame()
maintableIncomegroup["Category"] = t1Incomegroup["Income group"]
maintableIncomegroup["Count"] = t1IncomegroupCount["Population2010"]["count"]
maintableIncomegroup["Population2010"] = t1Incomegroup["Population2010"]["sum"]
maintableIncomegroup["popChangein2010_2030"] = t1Incomegroup["PopChange_2010-2030"]["sum"]
maintableIncomegroup["UrbanPopulation2010"] = t1Incomegroup["UrbanPopulation2010"]["sum"]
maintableIncomegroup["urbanPopChange2010_2030"] = t1Incomegroup["UrbanPopulation2030"]["sum"] - t1Incomegroup["UrbanPopulation2010"]["sum"]
maintableIncomegroup["UrbanPopulation_20YearLag2030"] = t1Incomegroup["UrbanPopulation_20YearLag2030"]["sum"]
maintableIncomegroup["NonUrbanPopulation_20YearLag2030"] = t1Incomegroup["NonUrbanPopulation_20YearLag2030"]["sum"]

### Append income group to regions
mainTable1 = maintableregion._append(maintableIncomegroup, ignore_index=True)
# save to csv
mainTable1.to_csv(results1 + r"\table1_2010and2030.csv")

##------------------------2010 - 2020---------------------------###

# main table 5  -- Region
t1regionCount = lowMidIncome[["Region", "Population2010"]].groupby('Region').agg(['count']).reset_index()
# Subset 2010 and 2020 
t1region = lowMidIncome[["Region", "Population2010","PopChange_2010-2020", "c1UrbanPopChange_2010-2020", "c2UrbanPopChange_2010-2020",  "c3UrbanPopChange_2010-2020"]].groupby('Region').agg(['sum']).reset_index()

maintableregion = pd.DataFrame()
maintableregion["Category"] = t1region["Region"]
maintableregion["Count"] = t1regionCount["Population2010"]["count"]
maintableregion["Population2010"] = t1region["Population2010"]["sum"]
maintableregion["popChangein2010_2020"] = t1region["PopChange_2010-2020"]["sum"]
maintableregion["c3UrbanPopChange_2010_2020"] = t1region["c3UrbanPopChange_2010-2020"]["sum"]
maintableregion["c2UrbanPopChange_2010_2020"] = t1region["c2UrbanPopChange_2010-2020"]["sum"]
maintableregion["c1UrbanPopChange_2010_2020"] = t1region["c1UrbanPopChange_2010-2020"]["sum"]

# main table 5  -- Income group
t1IncomegroupCount = lowMidIncome[["Income group", "Population2010"]].groupby('Income group').agg(['count']).reset_index()
# Subset 2010 and 2020 
t1Incomegroup = lowMidIncome[["Income group", "Population2010","PopChange_2010-2020", "c1UrbanPopChange_2010-2020", "c2UrbanPopChange_2010-2020",  "c3UrbanPopChange_2010-2020"]].groupby("Income group").agg(["sum"]).reset_index()

maintableIncomegroup = pd.DataFrame()
maintableIncomegroup["Category"] = t1Incomegroup["Income group"]
maintableIncomegroup["Count"] = t1IncomegroupCount["Population2010"]["count"]
maintableIncomegroup["Population2010"] = t1Incomegroup["Population2010"]["sum"]
maintableIncomegroup["popChangein2010_2020"] = t1Incomegroup["PopChange_2010-2020"]["sum"]
maintableIncomegroup["c3UrbanPopChange_2010_2020"] = t1Incomegroup["c3UrbanPopChange_2010-2020"]["sum"]
maintableIncomegroup["c2UrbanPopChange_2010_2020"] = t1Incomegroup["c2UrbanPopChange_2010-2020"]["sum"]
maintableIncomegroup["c1UrbanPopChange_2010_2020"] = t1Incomegroup["c1UrbanPopChange_2010-2020"]["sum"]
### Append income group to regions
mainTable1 = maintableregion._append(maintableIncomegroup, ignore_index=True)
# save to csv
mainTable1.to_csv(results1 + r"\table2_2010and2020.csv")



##----------------------------- 2020 - 2030--------------------#### save to csv

# main table 6  -- Region
t1regionCount = lowMidIncome[["Region", "Population2020"]].groupby('Region').agg(['count']).reset_index()
# Subset 2020 and 2030 
t1region = lowMidIncome[["Region", "Population2020","PopChange_2020-2030", "c1UrbanPopChange_2020-2030", "c2UrbanPopChange_2020-2030",  "c3UrbanPopChange_2020-2030"]].groupby('Region').agg(['sum']).reset_index()

maintableregion = pd.DataFrame()
maintableregion["Category"] = t1region["Region"]
maintableregion["Count"] = t1regionCount["Population2020"]["count"]
maintableregion["Population2020"] = t1region["Population2020"]["sum"]
maintableregion["popChangein2020_2030"] = t1region["PopChange_2020-2030"]["sum"]
maintableregion["c3UrbanPopChange_2020_2030"] = t1region["c3UrbanPopChange_2020-2030"]["sum"]
maintableregion["c2UrbanPopChange_2020_2030"] = t1region["c2UrbanPopChange_2020-2030"]["sum"]
maintableregion["c1UrbanPopChange_2020_2030"] = t1region["c1UrbanPopChange_2020-2030"]["sum"]

# main table 6  -- Income group
t1IncomegroupCount = lowMidIncome[["Income group", "Population2020"]].groupby('Income group').agg(['count']).reset_index()
# Subset 2020 and 2030 
t1Incomegroup = lowMidIncome[["Income group", "Population2020","PopChange_2020-2030", "c1UrbanPopChange_2020-2030", "c2UrbanPopChange_2020-2030",  "c3UrbanPopChange_2020-2030"]].groupby("Income group").agg(["sum"]).reset_index()

maintableIncomegroup = pd.DataFrame()
maintableIncomegroup["Category"] = t1Incomegroup["Income group"]
maintableIncomegroup["Count"] = t1IncomegroupCount["Population2020"]["count"]
maintableIncomegroup["Population2020"] = t1Incomegroup["Population2020"]["sum"]
maintableIncomegroup["popChangein2020_2030"] = t1Incomegroup["PopChange_2020-2030"]["sum"]
maintableIncomegroup["c3UrbanPopChange_2020_2030"] = t1Incomegroup["c3UrbanPopChange_2020-2030"]["sum"]
maintableIncomegroup["c2UrbanPopChange_2020_2030"] = t1Incomegroup["c2UrbanPopChange_2020-2030"]["sum"]
maintableIncomegroup["c1UrbanPopChange_2020_2030"] = t1Incomegroup["c1UrbanPopChange_2020-2030"]["sum"]
### Append income group to regions
mainTable1 = maintableregion._append(maintableIncomegroup, ignore_index=True)
# save to csv
mainTable1.to_csv(results1 + r"\table2_2020and2030.csv")



##----------------------------- 2000 - 2020--------------------#### save to csv

# main table 7  -- Region
t1regionCount = lowMidIncome[["Region", "Population2000"]].groupby('Region').agg(['count']).reset_index()
# Subset 2000 and 2020 
t1region = lowMidIncome[["Region", "Population2000","PopChange_2000-2020", "c1UrbanPopChange_2000-2020", "c2UrbanPopChange_2000-2020",  "c3UrbanPopChange_2000-2020"]].groupby('Region').agg(['sum']).reset_index()

maintableregion = pd.DataFrame()
maintableregion["Category"] = t1region["Region"]
maintableregion["Count"] = t1regionCount["Population2000"]["count"]
maintableregion["Population2000"] = t1region["Population2000"]["sum"]
maintableregion["popChangein2000_2020"] = t1region["PopChange_2000-2020"]["sum"]
maintableregion["c3UrbanPopChange_2000_2020"] = t1region["c3UrbanPopChange_2000-2020"]["sum"]
maintableregion["c2UrbanPopChange_2000_2020"] = t1region["c2UrbanPopChange_2000-2020"]["sum"]
maintableregion["c1UrbanPopChange_2000_2020"] = t1region["c1UrbanPopChange_2000-2020"]["sum"]

# main table 7  -- Income group
t1IncomegroupCount = lowMidIncome[["Income group", "Population2000"]].groupby('Income group').agg(['count']).reset_index()
# Subset 2000 and 2020 
t1Incomegroup = lowMidIncome[["Income group", "Population2000","PopChange_2000-2020", "c1UrbanPopChange_2000-2020", "c2UrbanPopChange_2000-2020",  "c3UrbanPopChange_2000-2020"]].groupby("Income group").agg(["sum"]).reset_index()

maintableIncomegroup = pd.DataFrame()
maintableIncomegroup["Category"] = t1Incomegroup["Income group"]
maintableIncomegroup["Count"] = t1IncomegroupCount["Population2000"]["count"]
maintableIncomegroup["Population2000"] = t1Incomegroup["Population2000"]["sum"]
maintableIncomegroup["popChangein2000_2020"] = t1Incomegroup["PopChange_2000-2020"]["sum"]
maintableIncomegroup["c3UrbanPopChange_2000_2020"] = t1Incomegroup["c3UrbanPopChange_2000-2020"]["sum"]
maintableIncomegroup["c2UrbanPopChange_2000_2020"] = t1Incomegroup["c2UrbanPopChange_2000-2020"]["sum"]
maintableIncomegroup["c1UrbanPopChange_2000_2020"] = t1Incomegroup["c1UrbanPopChange_2000-2020"]["sum"]
### Append income group to regions
mainTable1 = maintableregion._append(maintableIncomegroup, ignore_index=True)
# save to csv
mainTable1.to_csv(results1 + r"\table2_2000and2020.csv")



##------------------------2010 - 2030---------------------------###

# main table 8  -- Region
t1regionCount = lowMidIncome[["Region", "Population2010"]].groupby('Region').agg(['count']).reset_index()
# Subset 2010 and 2030 
t1region = lowMidIncome[["Region", "Population2010","PopChange_2010-2030", "c1UrbanPopChange_2010-2030", "c2UrbanPopChange_2010-2030",  "c3UrbanPopChange_2010-2030"]].groupby('Region').agg(['sum']).reset_index()

maintableregion = pd.DataFrame()
maintableregion["Category"] = t1region["Region"]
maintableregion["Count"] = t1regionCount["Population2010"]["count"]
maintableregion["Population2010"] = t1region["Population2010"]["sum"]
maintableregion["popChangein2010_2030"] = t1region["PopChange_2010-2030"]["sum"]
maintableregion["c3UrbanPopChange_2010_2030"] = t1region["c3UrbanPopChange_2010-2030"]["sum"]
maintableregion["c2UrbanPopChange_2010_2030"] = t1region["c2UrbanPopChange_2010-2030"]["sum"]
maintableregion["c1UrbanPopChange_2010_2030"] = t1region["c1UrbanPopChange_2010-2030"]["sum"]

# main table 8  -- Income group
t1IncomegroupCount = lowMidIncome[["Income group", "Population2010"]].groupby('Income group').agg(['count']).reset_index()
# Subset 2010 and 2030 
t1Incomegroup = lowMidIncome[["Income group", "Population2010","PopChange_2010-2030", "c1UrbanPopChange_2010-2030", "c2UrbanPopChange_2010-2030",  "c3UrbanPopChange_2010-2030"]].groupby("Income group").agg(["sum"]).reset_index()

maintableIncomegroup = pd.DataFrame()
maintableIncomegroup["Category"] = t1Incomegroup["Income group"]
maintableIncomegroup["Count"] = t1IncomegroupCount["Population2010"]["count"]
maintableIncomegroup["Population2010"] = t1Incomegroup["Population2010"]["sum"]
maintableIncomegroup["popChangein2010_2030"] = t1Incomegroup["PopChange_2010-2030"]["sum"]
maintableIncomegroup["c3UrbanPopChange_2010_2030"] = t1Incomegroup["c3UrbanPopChange_2010-2030"]["sum"]
maintableIncomegroup["c2UrbanPopChange_2010_2030"] = t1Incomegroup["c2UrbanPopChange_2010-2030"]["sum"]
maintableIncomegroup["c1UrbanPopChange_2010_2030"] = t1Incomegroup["c1UrbanPopChange_2010-2030"]["sum"]
### Append income group to regions
mainTable1 = maintableregion._append(maintableIncomegroup, ignore_index=True)
# save to csv
mainTable1.to_csv(results1 + r"\table2_2010and2030.csv")

print(f'Urban def 1 results saved at: {results1}')



# ------------------------------------ Tables generated from second population data with urban >= 21 ---------------------------------#

popData = pd.read_csv(results2 + r"\full_population_data.csv")  # import pop data 2

# drop high income countries
lowMidIncome = popData[popData["Income group"] != "High income"]


##------------------------2010 - 2020---------------------------###
# main table 1  -- Region
t1regionCount = lowMidIncome[["Region", "Population2010"]].groupby('Region').agg(['count']).reset_index()
# Subset 2010 and 2020 
t1region = lowMidIncome[["Region", "Population2010","PopChange_2010-2020", "UrbanPopulation2010", "UrbanPopulation2020",  "UrbanPopulation_10YearLag2020", "NonUrbanPopulation_10YearLag2020"]].groupby('Region').agg(['sum']).reset_index()

maintableregion = pd.DataFrame()
maintableregion["Category"] = t1region["Region"]
maintableregion["Count"] = t1regionCount["Population2010"]["count"]
maintableregion["Population2010"] = t1region["Population2010"]["sum"]
maintableregion["popChangein2010_2020"] = t1region["PopChange_2010-2020"]["sum"]
maintableregion["UrbanPopulation2010"] = t1region["UrbanPopulation2010"]["sum"]
maintableregion["urbanPopChange2010_2020"] = t1region["UrbanPopulation2020"]["sum"] - t1region["UrbanPopulation2010"]["sum"]
maintableregion["UrbanPopulation_10YearLag2020"] = t1region["UrbanPopulation_10YearLag2020"]["sum"]
maintableregion["NonUrbanPopulation_10YearLag2020"] = t1region["NonUrbanPopulation_10YearLag2020"]["sum"]

# main table 1  -- Income group
t1IncomegroupCount = lowMidIncome[["Income group", "Population2010"]].groupby('Income group').agg(['count']).reset_index()
# Subset 2010 and 2020 
t1Incomegroup = lowMidIncome[["Income group", "Population2010","PopChange_2010-2020", "UrbanPopulation2010", "UrbanPopulation2020", "UrbanPopulation_10YearLag2020", "NonUrbanPopulation_10YearLag2020"]].groupby("Income group").agg(["sum"]).reset_index()

maintableIncomegroup = pd.DataFrame()
maintableIncomegroup["Category"] = t1Incomegroup["Income group"]
maintableIncomegroup["Count"] = t1IncomegroupCount["Population2010"]["count"]
maintableIncomegroup["Population2010"] = t1Incomegroup["Population2010"]["sum"]
maintableIncomegroup["popChangein2010_2020"] = t1Incomegroup["PopChange_2010-2020"]["sum"]
maintableIncomegroup["UrbanPopulation2010"] = t1Incomegroup["UrbanPopulation2010"]["sum"]
maintableIncomegroup["urbanPopChange2010_2020"] = t1Incomegroup["UrbanPopulation2020"]["sum"] - t1Incomegroup["UrbanPopulation2010"]["sum"]
maintableIncomegroup["UrbanPopulation_10YearLag2020"] = t1Incomegroup["UrbanPopulation_10YearLag2020"]["sum"]
maintableIncomegroup["NonUrbanPopulation_10YearLag2020"] = t1Incomegroup["NonUrbanPopulation_10YearLag2020"]["sum"]

### Append income group to regions
mainTable1 = maintableregion._append(maintableIncomegroup, ignore_index=True)
# save to csv
mainTable1.to_csv(results2 + r"\table1_2010and2020.csv")

##----------------------------- 2020 - 2030--------------------#### save to csv
# main table 2  -- Region
t1regionCount = lowMidIncome[["Region", "Population2020"]].groupby('Region').agg(['count']).reset_index()
# Subset 2020 and 2030 
t1region = lowMidIncome[["Region", "Population2020","PopChange_2020-2030", "UrbanPopulation2020", "UrbanPopulation2030", "UrbanPopulation_10YearLag2030", "NonUrbanPopulation_10YearLag2030"]].groupby('Region').agg(['sum']).reset_index()

maintableregion = pd.DataFrame()
maintableregion["Category"] = t1region["Region"]
maintableregion["Count"] = t1regionCount["Population2020"]["count"]
maintableregion["Population2020"] = t1region["Population2020"]["sum"]
maintableregion["popChangein2020_2030"] = t1region["PopChange_2020-2030"]["sum"]
maintableregion["UrbanPopulation2020"] = t1region["UrbanPopulation2020"]["sum"]
maintableregion["urbanPopChange2020_2030"] = t1region["UrbanPopulation2030"]["sum"] - t1region["UrbanPopulation2020"]["sum"]
maintableregion["UrbanPopulation_10YearLag2030"] = t1region["UrbanPopulation_10YearLag2030"]["sum"]
maintableregion["NonUrbanPopulation_10YearLag2030"] = t1region["NonUrbanPopulation_10YearLag2030"]["sum"]

# main table 2  -- Income group
t1IncomegroupCount = lowMidIncome[["Income group", "Population2020"]].groupby('Income group').agg(['count']).reset_index()
# Subset 2020 and 2030 
t1Incomegroup = lowMidIncome[["Income group", "Population2020","PopChange_2020-2030", "UrbanPopulation2020", "UrbanPopulation2030", "UrbanPopulation_10YearLag2030", "NonUrbanPopulation_10YearLag2030"]].groupby("Income group").agg(["sum"]).reset_index()

maintableIncomegroup = pd.DataFrame()
maintableIncomegroup["Category"] = t1Incomegroup["Income group"]
maintableIncomegroup["Count"] = t1IncomegroupCount["Population2020"]["count"]
maintableIncomegroup["Population2020"] = t1Incomegroup["Population2020"]["sum"]
maintableIncomegroup["popChangein2020_2030"] = t1Incomegroup["PopChange_2020-2030"]["sum"]
maintableIncomegroup["UrbanPopulation2020"] = t1Incomegroup["UrbanPopulation2020"]["sum"]
maintableIncomegroup["urbanPopChange2020_2030"] = t1Incomegroup["UrbanPopulation2030"]["sum"] - t1Incomegroup["UrbanPopulation2020"]["sum"]
maintableIncomegroup["UrbanPopulation_10YearLag2030"] = t1Incomegroup["UrbanPopulation_10YearLag2030"]["sum"]
maintableIncomegroup["NonUrbanPopulation_10YearLag2030"] = t1Incomegroup["NonUrbanPopulation_10YearLag2030"]["sum"]

### Append income group to regions
mainTable1 = maintableregion._append(maintableIncomegroup, ignore_index=True)
# save to csv
mainTable1.to_csv(results2 + r"\table1_2020and2030.csv")


##----------------------------- 2000 - 2020--------------------#### save to csv
# main table 3  -- Region
t1regionCount = lowMidIncome[["Region", "Population2000"]].groupby('Region').agg(['count']).reset_index()
# Subset 2000 and 2020 
t1region = lowMidIncome[["Region", "Population2000","PopChange_2000-2020", "UrbanPopulation2000", "UrbanPopulation2020", "UrbanPopulation_20YearLag2020", "NonUrbanPopulation_20YearLag2020"]].groupby('Region').agg(['sum']).reset_index()

maintableregion = pd.DataFrame()
maintableregion["Category"] = t1region["Region"]
maintableregion["Count"] = t1regionCount["Population2000"]["count"]
maintableregion["Population2000"] = t1region["Population2000"]["sum"]
maintableregion["popChangein2000_2020"] = t1region["PopChange_2000-2020"]["sum"]
maintableregion["UrbanPopulation2000"] = t1region["UrbanPopulation2000"]["sum"]
maintableregion["urbanPopChange2000_2020"] = t1region["UrbanPopulation2020"]["sum"] - t1region["UrbanPopulation2000"]["sum"]
maintableregion["UrbanPopulation_20YearLag2020"] = t1region["UrbanPopulation_20YearLag2020"]["sum"]
maintableregion["NonUrbanPopulation_20YearLag2020"] = t1region["NonUrbanPopulation_20YearLag2020"]["sum"]

# main table 3  -- Income group
t1IncomegroupCount = lowMidIncome[["Income group", "Population2000"]].groupby('Income group').agg(['count']).reset_index()
# Subset 2020 and 2030 
t1Incomegroup = lowMidIncome[["Income group", "Population2000","PopChange_2000-2020", "UrbanPopulation2000", "UrbanPopulation2020", "UrbanPopulation_20YearLag2020", "NonUrbanPopulation_20YearLag2020"]].groupby("Income group").agg(["sum"]).reset_index()

maintableIncomegroup = pd.DataFrame()
maintableIncomegroup["Category"] = t1Incomegroup["Income group"]
maintableIncomegroup["Count"] = t1IncomegroupCount["Population2000"]["count"]
maintableIncomegroup["Population2000"] = t1Incomegroup["Population2000"]["sum"]
maintableIncomegroup["popChangein2000_2020"] = t1Incomegroup["PopChange_2000-2020"]["sum"]
maintableIncomegroup["UrbanPopulation2000"] = t1Incomegroup["UrbanPopulation2000"]["sum"]
maintableIncomegroup["urbanPopChange2000_2020"] = t1Incomegroup["UrbanPopulation2020"]["sum"] - t1Incomegroup["UrbanPopulation2000"]["sum"]
maintableIncomegroup["UrbanPopulation_20YearLag2020"] = t1Incomegroup["UrbanPopulation_20YearLag2020"]["sum"]
maintableIncomegroup["NonUrbanPopulation_20YearLag2020"] = t1Incomegroup["NonUrbanPopulation_20YearLag2020"]["sum"]

### Append income group to regions
mainTable1 = maintableregion._append(maintableIncomegroup, ignore_index=True)
# save to csv
mainTable1.to_csv(results2 + r"\table1_2000and2020.csv")



##----------------------------- 2010 - 2030--------------------#### save to csv
# main table 4  -- Region
t1regionCount = lowMidIncome[["Region", "Population2010"]].groupby('Region').agg(['count']).reset_index()
# Subset 2010 and 2030 
t1region = lowMidIncome[["Region", "Population2010","PopChange_2010-2030", "UrbanPopulation2010", "UrbanPopulation2030", "UrbanPopulation_20YearLag2030", "NonUrbanPopulation_20YearLag2030"]].groupby('Region').agg(['sum']).reset_index()

maintableregion = pd.DataFrame()
maintableregion["Category"] = t1region["Region"]
maintableregion["Count"] = t1regionCount["Population2010"]["count"]
maintableregion["Population2010"] = t1region["Population2010"]["sum"]
maintableregion["popChangein2010_2030"] = t1region["PopChange_2010-2030"]["sum"]
maintableregion["UrbanPopulation2010"] = t1region["UrbanPopulation2010"]["sum"]
maintableregion["urbanPopChange2010_2030"] = t1region["UrbanPopulation2030"]["sum"] - t1region["UrbanPopulation2010"]["sum"]
maintableregion["UrbanPopulation_20YearLag2030"] = t1region["UrbanPopulation_20YearLag2030"]["sum"]
maintableregion["NonUrbanPopulation_20YearLag2030"] = t1region["NonUrbanPopulation_20YearLag2030"]["sum"]

# main table 4  -- Income group
t1IncomegroupCount = lowMidIncome[["Income group", "Population2010"]].groupby('Income group').agg(['count']).reset_index()
# Subset 2020 and 2030 
t1Incomegroup = lowMidIncome[["Income group", "Population2010","PopChange_2010-2030", "UrbanPopulation2010", "UrbanPopulation2030", "UrbanPopulation_20YearLag2030", "NonUrbanPopulation_20YearLag2030"]].groupby("Income group").agg(["sum"]).reset_index()

maintableIncomegroup = pd.DataFrame()
maintableIncomegroup["Category"] = t1Incomegroup["Income group"]
maintableIncomegroup["Count"] = t1IncomegroupCount["Population2010"]["count"]
maintableIncomegroup["Population2010"] = t1Incomegroup["Population2010"]["sum"]
maintableIncomegroup["popChangein2010_2030"] = t1Incomegroup["PopChange_2010-2030"]["sum"]
maintableIncomegroup["UrbanPopulation2010"] = t1Incomegroup["UrbanPopulation2010"]["sum"]
maintableIncomegroup["urbanPopChange2010_2030"] = t1Incomegroup["UrbanPopulation2030"]["sum"] - t1Incomegroup["UrbanPopulation2010"]["sum"]
maintableIncomegroup["UrbanPopulation_20YearLag2030"] = t1Incomegroup["UrbanPopulation_20YearLag2030"]["sum"]
maintableIncomegroup["NonUrbanPopulation_20YearLag2030"] = t1Incomegroup["NonUrbanPopulation_20YearLag2030"]["sum"]

### Append income group to regions
mainTable1 = maintableregion._append(maintableIncomegroup, ignore_index=True)
# save to csv
mainTable1.to_csv(results2 + r"\table1_2010and2030.csv")

##------------------------2010 - 2020---------------------------###

# main table 5  -- Region
t1regionCount = lowMidIncome[["Region", "Population2010"]].groupby('Region').agg(['count']).reset_index()
# Subset 2010 and 2020 
t1region = lowMidIncome[["Region", "Population2010","PopChange_2010-2020", "c1UrbanPopChange_2010-2020", "c2UrbanPopChange_2010-2020",  "c3UrbanPopChange_2010-2020"]].groupby('Region').agg(['sum']).reset_index()

maintableregion = pd.DataFrame()
maintableregion["Category"] = t1region["Region"]
maintableregion["Count"] = t1regionCount["Population2010"]["count"]
maintableregion["Population2010"] = t1region["Population2010"]["sum"]
maintableregion["popChangein2010_2020"] = t1region["PopChange_2010-2020"]["sum"]
maintableregion["c3UrbanPopChange_2010_2020"] = t1region["c3UrbanPopChange_2010-2020"]["sum"]
maintableregion["c2UrbanPopChange_2010_2020"] = t1region["c2UrbanPopChange_2010-2020"]["sum"]
maintableregion["c1UrbanPopChange_2010_2020"] = t1region["c1UrbanPopChange_2010-2020"]["sum"]

# main table 5  -- Income group
t1IncomegroupCount = lowMidIncome[["Income group", "Population2010"]].groupby('Income group').agg(['count']).reset_index()
# Subset 2010 and 2020 
t1Incomegroup = lowMidIncome[["Income group", "Population2010","PopChange_2010-2020", "c1UrbanPopChange_2010-2020", "c2UrbanPopChange_2010-2020",  "c3UrbanPopChange_2010-2020"]].groupby("Income group").agg(["sum"]).reset_index()

maintableIncomegroup = pd.DataFrame()
maintableIncomegroup["Category"] = t1Incomegroup["Income group"]
maintableIncomegroup["Count"] = t1IncomegroupCount["Population2010"]["count"]
maintableIncomegroup["Population2010"] = t1Incomegroup["Population2010"]["sum"]
maintableIncomegroup["popChangein2010_2020"] = t1Incomegroup["PopChange_2010-2020"]["sum"]
maintableIncomegroup["c3UrbanPopChange_2010_2020"] = t1Incomegroup["c3UrbanPopChange_2010-2020"]["sum"]
maintableIncomegroup["c2UrbanPopChange_2010_2020"] = t1Incomegroup["c2UrbanPopChange_2010-2020"]["sum"]
maintableIncomegroup["c1UrbanPopChange_2010_2020"] = t1Incomegroup["c1UrbanPopChange_2010-2020"]["sum"]
### Append income group to regions
mainTable1 = maintableregion._append(maintableIncomegroup, ignore_index=True)
# save to csv
mainTable1.to_csv(results2 + r"\table2_2010and2020.csv")



##----------------------------- 2020 - 2030--------------------#### save to csv

# main table 6  -- Region
t1regionCount = lowMidIncome[["Region", "Population2020"]].groupby('Region').agg(['count']).reset_index()
# Subset 2020 and 2030 
t1region = lowMidIncome[["Region", "Population2020","PopChange_2020-2030", "c1UrbanPopChange_2020-2030", "c2UrbanPopChange_2020-2030",  "c3UrbanPopChange_2020-2030"]].groupby('Region').agg(['sum']).reset_index()

maintableregion = pd.DataFrame()
maintableregion["Category"] = t1region["Region"]
maintableregion["Count"] = t1regionCount["Population2020"]["count"]
maintableregion["Population2020"] = t1region["Population2020"]["sum"]
maintableregion["popChangein2020_2030"] = t1region["PopChange_2020-2030"]["sum"]
maintableregion["c3UrbanPopChange_2020_2030"] = t1region["c3UrbanPopChange_2020-2030"]["sum"]
maintableregion["c2UrbanPopChange_2020_2030"] = t1region["c2UrbanPopChange_2020-2030"]["sum"]
maintableregion["c1UrbanPopChange_2020_2030"] = t1region["c1UrbanPopChange_2020-2030"]["sum"]

# main table 6  -- Income group
t1IncomegroupCount = lowMidIncome[["Income group", "Population2020"]].groupby('Income group').agg(['count']).reset_index()
# Subset 2020 and 2030 
t1Incomegroup = lowMidIncome[["Income group", "Population2020","PopChange_2020-2030", "c1UrbanPopChange_2020-2030", "c2UrbanPopChange_2020-2030",  "c3UrbanPopChange_2020-2030"]].groupby("Income group").agg(["sum"]).reset_index()

maintableIncomegroup = pd.DataFrame()
maintableIncomegroup["Category"] = t1Incomegroup["Income group"]
maintableIncomegroup["Count"] = t1IncomegroupCount["Population2020"]["count"]
maintableIncomegroup["Population2020"] = t1Incomegroup["Population2020"]["sum"]
maintableIncomegroup["popChangein2020_2030"] = t1Incomegroup["PopChange_2020-2030"]["sum"]
maintableIncomegroup["c3UrbanPopChange_2020_2030"] = t1Incomegroup["c3UrbanPopChange_2020-2030"]["sum"]
maintableIncomegroup["c2UrbanPopChange_2020_2030"] = t1Incomegroup["c2UrbanPopChange_2020-2030"]["sum"]
maintableIncomegroup["c1UrbanPopChange_2020_2030"] = t1Incomegroup["c1UrbanPopChange_2020-2030"]["sum"]
### Append income group to regions
mainTable1 = maintableregion._append(maintableIncomegroup, ignore_index=True)
# save to csv
mainTable1.to_csv(results2 + r"\table2_2020and2030.csv")



##----------------------------- 2000 - 2020--------------------#### save to csv

# main table 6  -- Region
t1regionCount = lowMidIncome[["Region", "Population2000"]].groupby('Region').agg(['count']).reset_index()
# Subset 2000 and 2020 
t1region = lowMidIncome[["Region", "Population2000","PopChange_2000-2020", "c1UrbanPopChange_2000-2020", "c2UrbanPopChange_2000-2020",  "c3UrbanPopChange_2000-2020"]].groupby('Region').agg(['sum']).reset_index()

maintableregion = pd.DataFrame()
maintableregion["Category"] = t1region["Region"]
maintableregion["Count"] = t1regionCount["Population2000"]["count"]
maintableregion["Population2000"] = t1region["Population2000"]["sum"]
maintableregion["popChangein2000_2020"] = t1region["PopChange_2000-2020"]["sum"]
maintableregion["c3UrbanPopChange_2000_2020"] = t1region["c3UrbanPopChange_2000-2020"]["sum"]
maintableregion["c2UrbanPopChange_2000_2020"] = t1region["c2UrbanPopChange_2000-2020"]["sum"]
maintableregion["c1UrbanPopChange_2000_2020"] = t1region["c1UrbanPopChange_2000-2020"]["sum"]

# main table 7  -- Income group
t1IncomegroupCount = lowMidIncome[["Income group", "Population2000"]].groupby('Income group').agg(['count']).reset_index()
# Subset 2000 and 2020 
t1Incomegroup = lowMidIncome[["Income group", "Population2000","PopChange_2000-2020", "c1UrbanPopChange_2000-2020", "c2UrbanPopChange_2000-2020",  "c3UrbanPopChange_2000-2020"]].groupby("Income group").agg(["sum"]).reset_index()

maintableIncomegroup = pd.DataFrame()
maintableIncomegroup["Category"] = t1Incomegroup["Income group"]
maintableIncomegroup["Count"] = t1IncomegroupCount["Population2000"]["count"]
maintableIncomegroup["Population2000"] = t1Incomegroup["Population2000"]["sum"]
maintableIncomegroup["popChangein2000_2020"] = t1Incomegroup["PopChange_2000-2020"]["sum"]
maintableIncomegroup["c3UrbanPopChange_2000_2020"] = t1Incomegroup["c3UrbanPopChange_2000-2020"]["sum"]
maintableIncomegroup["c2UrbanPopChange_2000_2020"] = t1Incomegroup["c2UrbanPopChange_2000-2020"]["sum"]
maintableIncomegroup["c1UrbanPopChange_2000_2020"] = t1Incomegroup["c1UrbanPopChange_2000-2020"]["sum"]
### Append income group to regions
mainTable1 = maintableregion._append(maintableIncomegroup, ignore_index=True)
# save to csv
mainTable1.to_csv(results2 + r"\table2_2000and2020.csv")



##------------------------2010 - 2030---------------------------###

# main table 8  -- Region
t1regionCount = lowMidIncome[["Region", "Population2010"]].groupby('Region').agg(['count']).reset_index()
# Subset 2010 and 2030 
t1region = lowMidIncome[["Region", "Population2010","PopChange_2010-2030", "c1UrbanPopChange_2010-2030", "c2UrbanPopChange_2010-2030",  "c3UrbanPopChange_2010-2030"]].groupby('Region').agg(['sum']).reset_index()

maintableregion = pd.DataFrame()
maintableregion["Category"] = t1region["Region"]
maintableregion["Count"] = t1regionCount["Population2010"]["count"]
maintableregion["Population2010"] = t1region["Population2010"]["sum"]
maintableregion["popChangein2010_2030"] = t1region["PopChange_2010-2030"]["sum"]
maintableregion["c3UrbanPopChange_2010_2030"] = t1region["c3UrbanPopChange_2010-2030"]["sum"]
maintableregion["c2UrbanPopChange_2010_2030"] = t1region["c2UrbanPopChange_2010-2030"]["sum"]
maintableregion["c1UrbanPopChange_2010_2030"] = t1region["c1UrbanPopChange_2010-2030"]["sum"]

# main table 8  -- Income group
t1IncomegroupCount = lowMidIncome[["Income group", "Population2010"]].groupby('Income group').agg(['count']).reset_index()
# Subset 2010 and 2030 
t1Incomegroup = lowMidIncome[["Income group", "Population2010","PopChange_2010-2030", "c1UrbanPopChange_2010-2030", "c2UrbanPopChange_2010-2030",  "c3UrbanPopChange_2010-2030"]].groupby("Income group").agg(["sum"]).reset_index()

maintableIncomegroup = pd.DataFrame()
maintableIncomegroup["Category"] = t1Incomegroup["Income group"]
maintableIncomegroup["Count"] = t1IncomegroupCount["Population2010"]["count"]
maintableIncomegroup["Population2010"] = t1Incomegroup["Population2010"]["sum"]
maintableIncomegroup["popChangein2010_2030"] = t1Incomegroup["PopChange_2010-2030"]["sum"]
maintableIncomegroup["c3UrbanPopChange_2010_2030"] = t1Incomegroup["c3UrbanPopChange_2010-2030"]["sum"]
maintableIncomegroup["c2UrbanPopChange_2010_2030"] = t1Incomegroup["c2UrbanPopChange_2010-2030"]["sum"]
maintableIncomegroup["c1UrbanPopChange_2010_2030"] = t1Incomegroup["c1UrbanPopChange_2010-2030"]["sum"]
### Append income group to regions
mainTable1 = maintableregion._append(maintableIncomegroup, ignore_index=True)
# save to csv
mainTable1.to_csv(results2 + r"\table2_2010and2030.csv")


print(f'Urban def 2 results saved at: {results2}')