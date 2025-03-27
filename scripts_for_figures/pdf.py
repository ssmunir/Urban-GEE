import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import pandas as pd

# Expand data to original sample
data = pd.read_csv(r"C:\Users\auuser\Documents\Munir\Urbanization Analysis\GEE\archive\Nigeria_unbuilt_nres.csv")

# Calculate total frequency
total_freq = sum(data.frequency)

# Calculate probability density
pdf_values = [f / total_freq for f in data.frequency]

# Plotting
plt.figure(figsize=(10,6))
plt.plot(data.percent_unbuilt, pdf_values, color='blue', lw=2)
plt.xlabel("% land not developed within 1km²")
plt.ylabel("Probability Density")
plt.title("Kernel Density Estimation of Urbanization")
plt.grid(True)
plt.show()
