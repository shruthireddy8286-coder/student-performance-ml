"""
train_supervised.py  (ENHANCED)
--------------------------------
Trains a Random Forest Classifier (Supervised Learning) to predict
student performance category: Good / Average / Poor.

NEW in this version:
  1. 5-fold cross-validation (not just one train/test split) — shows
     the model's accuracy is stable, not a lucky split.
  2. A confusion matrix, saved as an image, so you can SHOW where the
     model gets confused (e.g. Average vs Poor) instead of just
     quoting a single accuracy number.
  3. A side-by-side comparison against Logistic Regression and SVM —
     useful evidence for your report/viva that Random Forest was a
     deliberate, justified choice.

Run:
    python train_supervised.py
Outputs:
    models/random_forest.pkl
    models/scaler.pkl
    reports/confusion_matrix_rf.png
    reports/feature_importance.png
    reports/model_comparison.png
    reports/model_comparison.csv
"""

import os
import csv
import shutil
import datetime
import joblib
import numpy as np
import matplotlib
matplotlib.use("Agg")  # no GUI needed, just save PNG files
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay

from preprocessing import load_dataset, fit_scaler, FEATURE_COLUMNS, LABEL_COLUMN, LABEL_ORDER

os.makedirs("reports", exist_ok=True)
os.makedirs("models/versions", exist_ok=True)

print("Loading and preprocessing dataset...")
df = load_dataset()

print("Fitting scaler on features...")
scaler, X_scaled = fit_scaler(df)
y = df[LABEL_COLUMN]

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# ------------------------------------------------------------------
# 1. Hyperparameter tuning with GridSearchCV
#    Instead of hand-picking n_estimators=200, max_depth=8, we search
#    a small grid and let cross-validation pick the best combination.
#    This is real, defensible model optimization rather than guessing.
# ------------------------------------------------------------------
print("\nRunning GridSearchCV to tune Random Forest hyperparameters...")
param_grid = {
    "n_estimators": [100, 200, 300],
    "max_depth": [6, 8, 10, None],
    "min_samples_split": [2, 5],
}
base_rf = RandomForestClassifier(random_state=42, class_weight="balanced")
grid_search = GridSearchCV(base_rf, param_grid, cv=cv, scoring="accuracy", n_jobs=-1)
grid_search.fit(X_train, y_train)

print(f"Best hyperparameters found: {grid_search.best_params_}")
print(f"Best cross-validation accuracy during search: {grid_search.best_score_*100:.2f}%")

rf_model = grid_search.best_estimator_

with open("reports/gridsearch_results.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["params", "mean_test_score", "std_test_score"])
    results = grid_search.cv_results_
    for params, mean, std in zip(results["params"], results["mean_test_score"], results["std_test_score"]):
        writer.writerow([params, round(mean, 4), round(std, 4)])
print("Saved reports/gridsearch_results.csv (all combinations tried)")

# ------------------------------------------------------------------
# 2. Evaluate the TUNED model
# ------------------------------------------------------------------
y_pred = rf_model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\nHold-out Test Accuracy (tuned model): {acc*100:.2f}%\n")
print(classification_report(y_test, y_pred))

print("Running 5-fold cross-validation on the tuned model...")
cv_scores = cross_val_score(rf_model, X_scaled, y, cv=cv)
print(f"Cross-validation scores: {np.round(cv_scores, 4)}")
print(f"Mean CV accuracy: {cv_scores.mean()*100:.2f}%  (+/- {cv_scores.std()*100:.2f}%)")

# ------------------------------------------------------------------
# 3. Confusion matrix — saved as an image for your report/viva
# ------------------------------------------------------------------
cm = confusion_matrix(y_test, y_pred, labels=LABEL_ORDER)
fig, ax = plt.subplots(figsize=(5, 4.5))
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=LABEL_ORDER)
disp.plot(ax=ax, cmap="Blues", colorbar=False)
ax.set_title("Random Forest — Confusion Matrix")
plt.tight_layout()
plt.savefig("reports/confusion_matrix_rf.png", dpi=150)
plt.close()
print("Saved reports/confusion_matrix_rf.png")

# ------------------------------------------------------------------
# 4. Feature importance
# ------------------------------------------------------------------
importances = sorted(zip(FEATURE_COLUMNS, rf_model.feature_importances_), key=lambda x: -x[1])
print("\nFeature importance (most -> least influential):")
for name, imp in importances:
    print(f"  {name:25s} {imp:.3f}")

fig, ax = plt.subplots(figsize=(6, 4))
names = [n for n, _ in importances]
vals = [v for _, v in importances]
ax.barh(names[::-1], vals[::-1], color="#3454D1")
ax.set_xlabel("Importance")
ax.set_title("Random Forest — Feature Importance")
plt.tight_layout()
plt.savefig("reports/feature_importance.png", dpi=150)
plt.close()
print("Saved reports/feature_importance.png")

# ------------------------------------------------------------------
# 5. Compare against Logistic Regression and SVM
#    (Justifies WHY Random Forest was chosen as the main model.)
# ------------------------------------------------------------------
print("\nComparing against other supervised models...")
candidates = {
    "Random Forest": rf_model,
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "SVM (RBF kernel)": SVC(kernel="rbf", probability=True, random_state=42),
}

results = []
for name, model in candidates.items():
    if name != "Random Forest":
        model.fit(X_train, y_train)
    pred = model.predict(X_test)
    test_acc = accuracy_score(y_test, pred)
    cv_acc = cross_val_score(model, X_scaled, y, cv=cv).mean()
    results.append({"model": name, "test_accuracy": test_acc, "cv_accuracy": cv_acc})
    print(f"  {name:22s}  test_acc={test_acc*100:5.2f}%   cv_acc={cv_acc*100:5.2f}%")

with open("reports/model_comparison.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["model", "test_accuracy", "cv_accuracy"])
    writer.writeheader()
    writer.writerows(results)

fig, ax = plt.subplots(figsize=(6, 4))
model_names = [r["model"] for r in results]
cv_accs = [r["cv_accuracy"] * 100 for r in results]
colors = ["#0EA894" if m == "Random Forest" else "#B7BCD6" for m in model_names]
ax.bar(model_names, cv_accs, color=colors)
ax.set_ylabel("Cross-validation Accuracy (%)")
ax.set_title("Supervised Model Comparison")
ax.set_ylim(0, 105)
for i, v in enumerate(cv_accs):
    ax.text(i, v + 1.5, f"{v:.1f}%", ha="center", fontsize=9)
plt.tight_layout()
plt.savefig("reports/model_comparison.png", dpi=150)
plt.close()
print("Saved reports/model_comparison.png and reports/model_comparison.csv")

# ------------------------------------------------------------------
# 6. Save the chosen production model (Random Forest) + scaler
# ------------------------------------------------------------------
joblib.dump(rf_model, "models/random_forest.pkl")
joblib.dump(scaler, "models/scaler.pkl")
print("\nSaved models/random_forest.pkl and models/scaler.pkl")

# ------------------------------------------------------------------
# 7. Model versioning — keep a timestamped copy every time we train,
#    instead of silently overwriting history. Lets you roll back if
#    a new training run ever performs worse than a previous one.
# ------------------------------------------------------------------
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
version_path = f"models/versions/random_forest_{timestamp}.pkl"
shutil.copy("models/random_forest.pkl", version_path)

version_log_path = "models/versions/version_log.csv"
log_exists = os.path.exists(version_log_path)
with open(version_log_path, "a", newline="") as f:
    writer = csv.writer(f)
    if not log_exists:
        writer.writerow(["timestamp", "model_file", "test_accuracy", "cv_mean_accuracy", "best_params"])
    writer.writerow([timestamp, version_path, round(acc, 4), round(cv_scores.mean(), 4), grid_search.best_params_])
print(f"Saved versioned copy: {version_path}")
print(f"Logged to {version_log_path}")
