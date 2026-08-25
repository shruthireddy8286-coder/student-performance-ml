"""
test_preprocessing.py
-----------------------
Basic automated tests for the shared preprocessing module. Run these
to confirm the core data pipeline behaves correctly — good evidence
of software engineering discipline beyond just training models.

Run from the ml/ folder:
    python -m pytest tests/ -v

Requires: pip install pytest
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import pytest

from preprocessing import (
    FEATURE_COLUMNS, LABEL_COLUMN, LABEL_ORDER,
    fit_scaler, scale_single_record,
)


def test_feature_columns_count():
    """There should be exactly 8 input features, as documented."""
    assert len(FEATURE_COLUMNS) == 8


def test_label_order_is_fixed():
    """Label order must stay Good, Average, Poor — the ANN's output
    neurons and the Flask API both depend on this exact order."""
    assert LABEL_ORDER == ["Good", "Average", "Poor"]


def test_fit_scaler_output_shape():
    """Scaling N rows of 8 features should produce an N x 8 array."""
    df = pd.DataFrame({col: np.random.uniform(0, 100, 20) for col in FEATURE_COLUMNS})
    scaler, X_scaled = fit_scaler(df)
    assert X_scaled.shape == (20, len(FEATURE_COLUMNS))


def test_fit_scaler_mean_near_zero():
    """A StandardScaler should center each feature's mean near 0."""
    df = pd.DataFrame({col: np.random.uniform(0, 100, 200) for col in FEATURE_COLUMNS})
    scaler, X_scaled = fit_scaler(df)
    assert np.allclose(X_scaled.mean(axis=0), 0, atol=1e-6)


def test_scale_single_record_shape():
    """Scaling one student's record should return a single row."""
    df = pd.DataFrame({col: np.random.uniform(0, 100, 50) for col in FEATURE_COLUMNS})
    scaler, _ = fit_scaler(df)

    record = {col: 75.0 for col in FEATURE_COLUMNS}
    scaled_row = scale_single_record(scaler, record)
    assert scaled_row.shape == (1, len(FEATURE_COLUMNS))


def test_scale_single_record_feature_order():
    """Regression test: feature order must stay consistent between
    training and single-record scaling, or predictions would silently
    use the wrong feature for the wrong slot (a classic ML bug)."""
    df = pd.DataFrame({col: np.random.uniform(0, 100, 50) for col in FEATURE_COLUMNS})
    scaler, _ = fit_scaler(df)

    # Give attendance a distinctly different value from the rest
    record = {col: 50.0 for col in FEATURE_COLUMNS}
    record["attendance"] = 100.0
    scaled_row = scale_single_record(scaler, record)

    attendance_idx = FEATURE_COLUMNS.index("attendance")
    # attendance=100 should scale to a HIGHER value than the other
    # features (which are all 50), proving the column mapping is correct
    other_indices = [i for i in range(len(FEATURE_COLUMNS)) if i != attendance_idx]
    assert scaled_row[0, attendance_idx] > max(scaled_row[0, i] for i in other_indices)


def test_missing_feature_raises_keyerror():
    """scale_single_record should fail loudly if a required feature
    is missing, rather than silently producing a wrong prediction."""
    df = pd.DataFrame({col: np.random.uniform(0, 100, 20) for col in FEATURE_COLUMNS})
    scaler, _ = fit_scaler(df)

    incomplete_record = {col: 50.0 for col in FEATURE_COLUMNS if col != "attendance"}
    with pytest.raises(KeyError):
        scale_single_record(scaler, incomplete_record)
