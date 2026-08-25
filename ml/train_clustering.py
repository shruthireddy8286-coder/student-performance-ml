"""
train_clustering.py  (ENHANCED)
---------------------------------
Unsupervised Learning: groups students into 3 clusters using K-Means
based purely on their feature similarity (NOT using final_result).

NEW in this version:
  - Elbow method plot (inertia vs K) — visually justifies why K=3 was
    chosen instead of just asserting it.
  - Silhouette score — a numeric measure of how well-separated the
    clusters are (closer to 1.0 = better separated clusters).

After clustering, we look at the AVERAGE attendance/marks of each
cluster and assign a human-readable label:
    High Performer / Average Performer / At-Risk Student

Run:
    python train_clustering.py
Outputs:
    models/kmeans.pkl
    models/cluster_labels.pkl   (maps cluster_number -> friendly name)
    reports/elbow_method.png
    reports/cluster_scatter.png
"""

import os
import numpy as np
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

from preprocessing import load_dataset, fit_scaler, FEATURE_COLUMNS

os.makedirs("reports", exist_ok=True)

print("Loading and preprocessing dataset...")
df = load_dataset()

# IMPORTANT: K-Means only sees the features, never the final_result label.
scaler, X_scaled = fit_scaler(df)

# ------------------------------------------------------------------
# 1. Elbow method — try K = 2..8 and plot inertia to justify K=3
# ------------------------------------------------------------------
print("Running elbow method (K=2..8)...")
k_range = range(2, 9)
inertias = []
silhouettes = []
for k in k_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    inertias.append(km.inertia_)
    silhouettes.append(silhouette_score(X_scaled, labels))
    print(f"  K={k}: inertia={km.inertia_:.1f}, silhouette={silhouettes[-1]:.3f}")

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].plot(list(k_range), inertias, marker="o", color="#3454D1")
axes[0].axvline(x=3, color="#E1524F", linestyle="--", label="Chosen K=3")
axes[0].set_xlabel("Number of clusters (K)")
axes[0].set_ylabel("Inertia (within-cluster variance)")
axes[0].set_title("Elbow Method")
axes[0].legend()

axes[1].plot(list(k_range), silhouettes, marker="o", color="#0EA894")
axes[1].axvline(x=3, color="#E1524F", linestyle="--", label="Chosen K=3")
axes[1].set_xlabel("Number of clusters (K)")
axes[1].set_ylabel("Silhouette Score")
axes[1].set_title("Silhouette Score by K")
axes[1].legend()

plt.tight_layout()
plt.savefig("reports/elbow_method.png", dpi=150)
plt.close()
print("Saved reports/elbow_method.png")

# ------------------------------------------------------------------
# 2. Final K-Means with K=3 (as used by the live prediction API)
# ------------------------------------------------------------------
print("\nRunning final K-Means with K=3...")
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
cluster_ids = kmeans.fit_predict(X_scaled)
final_silhouette = silhouette_score(X_scaled, cluster_ids)
print(f"Final silhouette score (K=3): {final_silhouette:.3f}")

df["cluster"] = cluster_ids

composite_cols = ["attendance", "assignment_score", "internal_marks",
                   "previous_semester_marks", "quiz_score",
                   "participation", "assignment_completion"]

cluster_strength = df.groupby("cluster")[composite_cols].mean().mean(axis=1)
ranked_clusters = cluster_strength.sort_values(ascending=False).index.tolist()

friendly_names = ["High Performer", "Average Performer", "At-Risk Student"]
cluster_label_map = {cluster_id: friendly_names[i] for i, cluster_id in enumerate(ranked_clusters)}

print("\nCluster summary (mean values):")
print(df.groupby("cluster")[composite_cols].mean().round(1))
print("\nAssigned cluster names based on average performance:")
for cid, name in cluster_label_map.items():
    print(f"  Cluster {cid} -> {name}")

# ------------------------------------------------------------------
# 3. 2D scatter plot of clusters (via PCA, since we have 8 features)
# ------------------------------------------------------------------
pca = PCA(n_components=2, random_state=42)
X_2d = pca.fit_transform(X_scaled)

color_map = {cid: c for cid, c in zip(ranked_clusters, ["#0EA894", "#3454D1", "#E1524F"])}
fig, ax = plt.subplots(figsize=(6, 5))
for cid in df["cluster"].unique():
    mask = df["cluster"] == cid
    ax.scatter(X_2d[mask, 0], X_2d[mask, 1],
               label=cluster_label_map[cid], color=color_map[cid], alpha=0.6, s=25)
ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.0f}% variance)")
ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.0f}% variance)")
ax.set_title("Student Clusters (PCA-reduced to 2D for visualization)")
ax.legend()
plt.tight_layout()
plt.savefig("reports/cluster_scatter.png", dpi=150)
plt.close()
print("Saved reports/cluster_scatter.png")

joblib.dump(kmeans, "models/kmeans.pkl")
joblib.dump(cluster_label_map, "models/cluster_labels.pkl")
print("\nSaved models/kmeans.pkl and models/cluster_labels.pkl")
