# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 05:16:06 2025

@author: auuser
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from adjustText import adjust_text

# Load data
# Note: Replace these paths with your actual paths when running the code
real = pd.read_csv(r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\temp_pop_verification\popwb.csv")
gee = pd.read_csv(r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\data\gen\urbanchange_summary_stats2.csv")
#geemod = pd.read_csv(r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\temp_pop_verification\Population_2020 (3).csv")
# Merge datasets
df = pd.merge(real, gee, how="inner", on="country")
# Create logarithmic columns for plottings
df["log2020"] = np.log(df["Population2020"])
df["log2020_real"] = np.log(df["Population2020_real"])

# Calculate the difference and ratio between Population2020 and Population2020_real
df["pop_diff"] = np.abs(df["log2020"] - df["log2020_real"])
df["pop_ratio"] = df["Population2020"] / df["Population2020_real"]
df["pop_diffexp"] = np.abs(df["Population2020"] - df["Population2020_real"])
# Calculate summary stats for the title
sumpop = round(sum(df['Population2020_real']) / 1e9, 1)
geepop = round(sum(df['Population2020']) / 1e9, 1)

# PLOT 1: Scatter plot with 45-degree line and point size based on difference
plt.figure(figsize=(20, 12))
sns.set_style("whitegrid")

# Create the scatter plot with point size based on the log difference
scatter = sns.scatterplot(
    data=df,
    x='log2020', 
    y='log2020_real',
    size='pop_diff',  # Size points by difference between the two values
    sizes=(50, 400),  # Range of point sizes
    hue='pop_diff',   # Color points by difference for added emphasis
    palette='viridis', # Use a color palette that shows the gradient well
    alpha=0.8
)

# Add a 45-degree line
x_min, x_max = plt.xlim()
y_min, y_max = plt.ylim()
max_val = max(x_max, y_max)
min_val = min(x_min, y_min)
plt.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=1.5, label='Perfect Match Line')

"""
# Add country labels with adjustment to prevent overlap
texts = []
for i, row in df.iterrows():
    texts.append(plt.text(row['log2020'], row['log2020_real'], row['country'], fontsize=10))
"""
texts = []
for i, row in df.iterrows():
    ratio = row['pop_ratio']
    # Only label countries with ratio outside the 10% range
    if ratio < 0.5 or ratio > 1.6:
        texts.append(plt.text(row['log2020'], row['log2020_real'], row['country'], fontsize=11))

# Improve styling
plt.xlabel('Log of GEE Population 2020', fontsize=16)
plt.ylabel('Log of Actual Population 2020', fontsize=16)
plt.title(f'Population Comparison by Country: World population = {sumpop}B and GEE pop = {geepop}B', fontsize=18)

# Add a legend
plt.legend(title='Population Difference', bbox_to_anchor=(1.05, 1), loc='upper left')

# Add grid
plt.grid(True, alpha=0.3, linestyle='--')

# Save Plot 1
#plt.tight_layout()
plt.savefig('population_comparison_log2.png', dpi=300, bbox_inches='tight')
plt.show()

# PLOT 2: Population Ratio Analysis
plt.figure(figsize=(20, 12))
sns.set_style("whitegrid")

# Create the ratio scatter plot
ratio_plot = sns.scatterplot(
    data=df,
    x='Population2020_real',  # Actual population on x-axis
    y='pop_ratio',            # Ratio on y-axis
    s=150,                    # Point size
    hue='pop_diff',          # Color by ratio
    palette='coolwarm',       # Use diverging palette centered around 1.0
    alpha=0.8
)

# Add a horizontal line at ratio = 1.0 (perfect match)
plt.axhline(y=1.0, color='r', linestyle='--', linewidth=1.5, label='Perfect Ratio (1.0)')

# Add labels only for countries with ratio < 0.9 or ratio > 1.1 (10% difference in either direction)
texts = []
for i, row in df.iterrows():
    ratio = row['pop_ratio']
    # Only label countries with ratio outside the 10% range
    if ratio < 0.5 or ratio > 1.6:
        texts.append(plt.text(row['Population2020_real'], row['pop_ratio'], row['country'], fontsize=12))

# Improve styling
plt.xlabel('Actual Population 2020', fontsize=16)
plt.ylabel('GEE Population / Actual Population Ratio', fontsize=16)
plt.title('Population Ratio vs Actual Population by Country', fontsize=18)

# Add logarithmic scale to x-axis for better visualization
plt.xscale('log')

# Set y-axis limits to focus on the important range
#plt.ylim(0.5, 1.5)  # Adjust as needed based on your data

# Add grid
plt.grid(True, alpha=0.3, linestyle='--')

# Add a legend
plt.legend(title='Population Log Diff.', bbox_to_anchor=(1.05, 1), loc='upper left')

# Save Plot 2
#plt.tight_layout()
plt.savefig('population_ratio_analysis2.png', dpi=300, bbox_inches='tight')
plt.show()