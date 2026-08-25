"""
generate_dataset.py
--------------------
Generates a synthetic but realistic student academic dataset for
training the Supervised (Random Forest), ANN and K-Means models.

This is for ACADEMIC / MINI-PROJECT DEMONSTRATION purposes only.
Run:
    python generate_dataset.py
Output:
    dataset/student_data.csv
"""

import numpy as np
import pandas as pd

np.random.seed(42)

N = 600  # number of synthetic student records


def make_student(category):
    """Generate one row of feature data biased towards a performance category.

    NOTE: standard deviations here are deliberately widened (compared to an
    earlier version of this script) so that Good/Average/Poor distributions
    overlap somewhat, the way real student data would. This makes the
    trained models' accuracy realistic (not a suspicious 100%) and gives
    the confusion matrix / explainability features something genuine to
    show, rather than a trivially separable toy dataset.
    """
    if category == "Good":
        attendance = np.random.normal(88, 9)
        assignment = np.random.normal(82, 11)
        internal = np.random.normal(79, 11)
        previous = np.random.normal(77, 11)
        study_hours = np.random.normal(4.2, 1.4)
        quiz = np.random.normal(81, 11)
        participation = np.random.normal(80, 12)
        completion = np.random.normal(90, 9)
    elif category == "Average":
        attendance = np.random.normal(72, 9)
        assignment = np.random.normal(65, 11)
        internal = np.random.normal(63, 11)
        previous = np.random.normal(62, 11)
        study_hours = np.random.normal(2.3, 1.1)
        quiz = np.random.normal(62, 11)
        participation = np.random.normal(60, 13)
        completion = np.random.normal(70, 13)
    else:  # Poor
        attendance = np.random.normal(55, 10)
        assignment = np.random.normal(48, 12)
        internal = np.random.normal(45, 12)
        previous = np.random.normal(47, 12)
        study_hours = np.random.normal(1.2, 0.9)
        quiz = np.random.normal(44, 12)
        participation = np.random.normal(43, 13)
        completion = np.random.normal(55, 14)

    def clip(v, lo, hi):
        return float(np.clip(v, lo, hi))

    return {
        "attendance": round(clip(attendance, 30, 100), 1),
        "assignment_score": round(clip(assignment, 0, 100), 1),
        "internal_marks": round(clip(internal, 0, 100), 1),
        "previous_semester_marks": round(clip(previous, 0, 100), 1),
        "study_hours": round(clip(study_hours, 0, 10), 2),
        "quiz_score": round(clip(quiz, 0, 100), 1),
        "participation": round(clip(participation, 0, 100), 1),
        "assignment_completion": round(clip(completion, 0, 100), 1),
        "final_result": category,
    }


rows = []
categories = ["Good", "Average", "Poor"]
# Roughly balanced classes so the model doesn't get lazy
counts = {"Good": int(N * 0.35), "Average": int(N * 0.40), "Poor": int(N * 0.25)}
counts["Poor"] += N - sum(counts.values())  # fix rounding

for cat, cnt in counts.items():
    for _ in range(cnt):
        rows.append(make_student(cat))

df = pd.DataFrame(rows)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # shuffle

# ------------------------------------------------------------------
# Add a small amount of LABEL NOISE (~4% of rows) to simulate real-world
# borderline students who could reasonably be labeled either way by a
# teacher (e.g. a student right on the edge between Average and Poor).
# This keeps the dataset from being trivially/artificially separable.
# ------------------------------------------------------------------
noise_fraction = 0.04
n_noisy = int(len(df) * noise_fraction)
noisy_idx = np.random.choice(df.index, size=n_noisy, replace=False)
neighbor = {"Good": "Average", "Average": "Poor", "Poor": "Average"}
for idx in noisy_idx:
    current = df.at[idx, "final_result"]
    df.at[idx, "final_result"] = neighbor[current]

df.insert(0, "student_row_id", range(1, len(df) + 1))

df.to_csv("dataset/student_data.csv", index=False)
print(f"Generated {len(df)} records -> dataset/student_data.csv")
print(df["final_result"].value_counts())
