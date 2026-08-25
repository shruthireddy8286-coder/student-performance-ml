"""
generate_eda.py
-----------------
Exploratory Data Analysis (EDA) — run this BEFORE training to
understand the dataset. Produces:
  1. A correlation heatmap between all 8 features (+ which features
     move together, e.g. does attendance correlate with quiz score?)
  2. Distribution plots of each feature, split by performance category

This is good material for the "Data Understanding" section of your
report, separate from model training/evaluation.

Run:
    python generate_eda.py
Outputs:
    reports/correlation_heatmap.png
    reports/feature_distributions.png
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from preprocessing import load_dataset, FEATURE_COLUMNS, LABEL_COLUMN

os.makedirs("reports", exist_ok=True)

print("Loading dataset...")
df = load_dataset()

# ------------------------------------------------------------------
# 1. Correlation heatmap
# ------------------------------------------------------------------
print("Computing feature correlations...")
corr = df[FEATURE_COLUMNS].corr()

fig, ax = plt.subplots(figsize=(8, 7))
sns.heatmap(
    corr, annot=True, fmt=".2f", cmap="coolwarm", center=0,
    square=True, linewidths=0.5, ax=ax, cbar_kws={"shrink": 0.8}
)
ax.set_title("Feature Correlation Heatmap")
plt.tight_layout()
plt.savefig("reports/correlation_heatmap.png", dpi=150)
plt.close()
print("Saved reports/correlation_heatmap.png")

print("\nStrongest feature correlations (excluding self-correlation):")
corr_pairs = corr.where(~corr.abs().eq(1.0)).unstack().dropna()
corr_pairs = corr_pairs[~corr_pairs.index.duplicated()].sort_values(key=abs, ascending=False)
for (f1, f2), val in corr_pairs.head(8).items():
    print(f"  {f1:25s} <-> {f2:25s}  r = {val:+.2f}")

# ------------------------------------------------------------------
# 2. Feature distributions by performance category
# ------------------------------------------------------------------
print("\nPlotting feature distributions by performance category...")
fig, axes = plt.subplots(2, 4, figsize=(16, 8))
axes = axes.flatten()
palette = {"Good": "#0EA894", "Average": "#E2A63B", "Poor": "#E1524F"}

for i, feature in enumerate(FEATURE_COLUMNS):
    sns.boxplot(data=df, x=LABEL_COLUMN, y=feature, ax=axes[i],
                order=["Good", "Average", "Poor"], palette=palette, hue=LABEL_COLUMN, legend=False)
    axes[i].set_title(feature.replace("_", " ").title())
    axes[i].set_xlabel("")

plt.tight_layout()
plt.savefig("reports/feature_distributions.png", dpi=150)
plt.close()
print("Saved reports/feature_distributions.png")

print("\nEDA complete. Use these images in your report's 'Data Understanding' section.")
