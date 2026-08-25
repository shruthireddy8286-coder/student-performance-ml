"""
preprocessing.py
----------------
Shared preprocessing logic used by ALL three model-training scripts
(train_supervised.py, train_ann.py, train_clustering.py) and by the
live prediction API (app.py).

Using ONE shared module guarantees that the exact same feature order
and scaling is used at both training time and prediction time, which
is a common mistake beginners make (train/serve skew).
"""

import pandas as pd
from sklearn.preprocessing import StandardScaler

# The 8 input features, in a FIXED order. Every model uses this order.
FEATURE_COLUMNS = [
    "attendance",
    "assignment_score",
    "internal_marks",
    "previous_semester_marks",
    "study_hours",
    "quiz_score",
    "participation",
    "assignment_completion",
]

LABEL_COLUMN = "final_result"
LABEL_ORDER = ["Good", "Average", "Poor"]  # fixed class order for ANN one-hot encoding


def load_dataset(path="dataset/student_data.csv"):
    df = pd.read_csv(path)

    # 1. Remove duplicates
    df = df.drop_duplicates()

    # 2. Handle missing values (simple median fill for numeric columns)
    for col in FEATURE_COLUMNS:
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())

    # 3. Drop rows with missing label (can't train on unknown label)
    df = df.dropna(subset=[LABEL_COLUMN])

    # 4. Basic outlier clipping (keep values within realistic 0-100 / 0-10 ranges)
    df["attendance"] = df["attendance"].clip(0, 100)
    df["assignment_score"] = df["assignment_score"].clip(0, 100)
    df["internal_marks"] = df["internal_marks"].clip(0, 100)
    df["previous_semester_marks"] = df["previous_semester_marks"].clip(0, 100)
    df["study_hours"] = df["study_hours"].clip(0, 12)
    df["quiz_score"] = df["quiz_score"].clip(0, 100)
    df["participation"] = df["participation"].clip(0, 100)
    df["assignment_completion"] = df["assignment_completion"].clip(0, 100)

    return df.reset_index(drop=True)


def fit_scaler(df):
    """Fit a StandardScaler on the feature columns and return (scaler, scaled_features)."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[FEATURE_COLUMNS])
    return scaler, X_scaled


def scale_single_record(scaler, record: dict):
    """
    record: dict with keys matching FEATURE_COLUMNS
    Returns a scaled 2D numpy array with 1 row, ready for model.predict().
    """
    row = pd.DataFrame([{col: record[col] for col in FEATURE_COLUMNS}])
    return scaler.transform(row[FEATURE_COLUMNS])
