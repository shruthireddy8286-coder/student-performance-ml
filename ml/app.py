"""
app.py
------
Flask ML API. PHP calls this service whenever the teacher clicks
"Predict Performance". This is the ONLY place where the trained
models are loaded and used for real-time inference.

Run:
    python app.py
Then it listens on:
    http://127.0.0.1:5000/predict   (POST, JSON body)
    http://127.0.0.1:5000/health    (GET)
"""

import os
import logging
from datetime import datetime

from flask import Flask, request, jsonify
import numpy as np
import joblib
import tensorflow as tf

from preprocessing import FEATURE_COLUMNS, LABEL_ORDER, scale_single_record

app = Flask(__name__)

# ------------------------------------------------------------------
# Request logging — every /predict call gets written to a log file
# with a timestamp, the input feature values, and the resulting
# prediction. Useful for debugging ("why did this student get Poor
# yesterday but Average today?") and as an audit trail.
# ------------------------------------------------------------------
os.makedirs("logs", exist_ok=True)
logger = logging.getLogger("prediction_log")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("logs/predictions.log")
file_handler.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))
logger.addHandler(file_handler)

# Human-friendly display names for each feature, used in explanations
FEATURE_DISPLAY_NAMES = {
    "attendance": "Attendance",
    "assignment_score": "Assignment Score",
    "internal_marks": "Internal Exam Marks",
    "previous_semester_marks": "Previous Semester Marks",
    "study_hours": "Study Hours",
    "quiz_score": "Quiz Score",
    "participation": "Class Participation",
    "assignment_completion": "Assignment Completion Rate",
}

# ------------------------------------------------------------------
# Load all trained models ONCE at startup (not per-request -> fast)
# ------------------------------------------------------------------
print("Loading trained models...")
scaler = joblib.load("models/scaler.pkl")
rf_model = joblib.load("models/random_forest.pkl")
ann_model = tf.keras.models.load_model("models/ann_model.keras")
kmeans_model = joblib.load("models/kmeans.pkl")
cluster_label_map = joblib.load("models/cluster_labels.pkl")
print("All models loaded successfully.")


# ------------------------------------------------------------------
# Per-student explainability.
# Not full SHAP (kept dependency-free and fast), but a genuinely
# informative approach: combine each feature's GLOBAL importance
# (from the trained Random Forest) with how far THIS student's
# value falls below the class-wide average (the scaled/z-score
# value produced by the same StandardScaler used in training).
# A feature that is both influential AND unusually low for this
# student is surfaced as a driving factor behind the prediction.
# ------------------------------------------------------------------
def explain_prediction(record, X_scaled_row):
    importances = dict(zip(FEATURE_COLUMNS, rf_model.feature_importances_))
    z_scores = dict(zip(FEATURE_COLUMNS, X_scaled_row))

    # Contribution score: only counts features that are BELOW average
    # (negative z-score) since those are what drag performance down.
    contributions = []
    for feature in FEATURE_COLUMNS:
        z = z_scores[feature]
        weakness = max(0.0, -z)  # 0 if at/above average, positive if below
        score = importances[feature] * weakness
        contributions.append((feature, score, z))

    contributions.sort(key=lambda x: -x[1])
    top_factors = [c for c in contributions if c[1] > 0][:3]

    explanations = []
    for feature, score, z in top_factors:
        display_name = FEATURE_DISPLAY_NAMES[feature]
        if z < -1.5:
            severity = "significantly below"
        elif z < -0.5:
            severity = "below"
        else:
            severity = "slightly below"
        explanations.append(
            f"{display_name} is {severity} the class average, "
            f"and is one of the more influential factors in this prediction."
        )

    if not explanations:
        explanations.append(
            "No single weak factor stands out — this student's values are "
            "at or above the class average across most measured features."
        )

    return explanations


# ------------------------------------------------------------------
# Project-defined risk rule (documented, not a medical/scientific cutoff)
# ------------------------------------------------------------------
def calculate_risk(poor_probability_pct):
    if poor_probability_pct >= 60:
        return "HIGH"
    elif poor_probability_pct >= 30:
        return "MEDIUM"
    else:
        return "LOW"


# ------------------------------------------------------------------
# Simple rule-based recommendation engine
# ------------------------------------------------------------------
def generate_recommendations(record):
    recs = []
    if record["attendance"] < 75:
        recs.append("Improve attendance")
    if record["assignment_completion"] < 75:
        recs.append("Complete pending assignments")
    if record["study_hours"] < 2:
        recs.append("Increase study hours")
    if record["quiz_score"] < 60:
        recs.append("Practice more quizzes")
    if record["participation"] < 60:
        recs.append("Participate more actively in class")
    if record["internal_marks"] < 60:
        recs.append("Attend additional/remedial classes")
    if not recs:
        recs.append("Keep up the good work — maintain current habits")
    return recs


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "ML API is running"})


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)

        # ---- Validate input ----
        missing = [c for c in FEATURE_COLUMNS if c not in data]
        if missing:
            return jsonify({"error": f"Missing fields: {missing}"}), 400

        try:
            record = {c: float(data[c]) for c in FEATURE_COLUMNS}
        except (TypeError, ValueError):
            return jsonify({"error": "All feature values must be numeric"}), 400

        # ---- Preprocess (SAME scaler used in training) ----
        X_scaled = scale_single_record(scaler, record)

        # ---- Supervised Learning: Random Forest ----
        rf_pred = rf_model.predict(X_scaled)[0]
        rf_proba = rf_model.predict_proba(X_scaled)[0]
        rf_classes = list(rf_model.classes_)
        rf_prob_map = {cls: round(float(p) * 100, 1) for cls, p in zip(rf_classes, rf_proba)}

        # ---- ANN prediction ----
        ann_proba = ann_model.predict(X_scaled, verbose=0)[0]
        ann_prob_map = {LABEL_ORDER[i]: round(float(ann_proba[i]) * 100, 1) for i in range(3)}
        ann_pred = LABEL_ORDER[int(np.argmax(ann_proba))]

        # ---- Combine: average RF + ANN probabilities for the final displayed % ----
        combined_prob = {
            label: round((rf_prob_map.get(label, 0) + ann_prob_map.get(label, 0)) / 2, 1)
            for label in LABEL_ORDER
        }
        final_prediction = max(combined_prob, key=combined_prob.get)

        # ---- Unsupervised Learning: K-Means cluster ----
        cluster_id = int(kmeans_model.predict(X_scaled)[0])
        cluster_name = cluster_label_map[cluster_id]

        # ---- Risk analysis (project-defined rule) ----
        poor_probability = combined_prob.get("Poor", 0)
        risk = calculate_risk(poor_probability)

        # ---- Recommendations ----
        recommendations = generate_recommendations(record)

        # ---- Per-student explainability ----
        explanations = explain_prediction(record, X_scaled[0])

        response = {
            "supervised_prediction": rf_pred,
            "ann_prediction": ann_pred,
            "final_prediction": final_prediction,
            "good_probability": combined_prob.get("Good", 0),
            "average_probability": combined_prob.get("Average", 0),
            "poor_probability": combined_prob.get("Poor", 0),
            "risk_level": risk,
            "cluster_id": cluster_id,
            "cluster_name": cluster_name,
            "recommendations": recommendations,
            "explanations": explanations,
        }

        logger.info(
            f"INPUT={record} | PREDICTION={final_prediction} | "
            f"RISK={risk} | CLUSTER={cluster_name} | "
            f"POOR_PROB={combined_prob.get('Poor', 0)}%"
        )

        return jsonify(response), 200

    except Exception as e:
        logger.info(f"ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
