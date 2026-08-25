# AI-Based Student Performance Prediction, Segmentation & At-Risk Detection

A complete mini-project demonstrating **Supervised Learning** (Random Forest),
**Artificial Neural Networks** (TensorFlow/Keras), and **Unsupervised Learning**
(K-Means Clustering) on structured student academic/behavioral data — wired up
to a real HTML/CSS/JS + PHP + MySQL web application.

```
STUDENT DATA → PREPROCESSING → ┬─ RANDOM FOREST ─┐
                                ├─ ANN            ├─→ RISK ANALYSIS → RECOMMENDATIONS → DASHBOARD
                                └─ K-MEANS       ─┘
```

---

## 1. What's inside

```
Student-Performance-ML/
├── frontend/          HTML/CSS/JS (login, dashboard, students, prediction, analytics)
├── backend/           PHP API (auth, CRUD, and the PHP → Flask bridge)
├── ml/                Python ML: dataset, preprocessing, training scripts, Flask API
├── database/          MySQL schema (student_ml_db.sql) + sample data
└── README.md          (this file)
```

The 3 ML concepts, and where to find each one:

| Concept | File | What it does |
|---|---|---|
| **Supervised Learning** | `ml/train_supervised.py` | Random Forest Classifier trained on labeled data (Good/Average/Poor known) |
| **Artificial Neural Network** | `ml/train_ann.py` | Keras Dense(64→32→16→3, softmax) network, same labeled data |
| **Unsupervised Learning** | `ml/train_clustering.py` | K-Means (K=3) groups students with NO label given — clusters are labeled afterwards by inspecting each cluster's average attendance/marks |

All three share one `ml/preprocessing.py` module and one `models/scaler.pkl`,
so training and live prediction always use identical feature scaling —
this avoids the classic "train/serve skew" bug.

---

## 1.5 What's new in this enhanced version

Beyond the original three ML concepts, this version adds:

| Feature | Where | Why it matters |
|---|---|---|
| **5-fold cross-validation** | `ml/train_supervised.py` | Proves accuracy is stable, not a lucky train/test split |
| **Confusion matrix (image)** | `ml/reports/confusion_matrix_rf.png` | Shows exactly where the model gets confused (e.g. Average vs Poor) |
| **Feature importance chart** | `ml/reports/feature_importance.png` | Visual evidence of which inputs matter most |
| **Model comparison** | `ml/reports/model_comparison.png` + `.csv` | Random Forest vs Logistic Regression vs SVM — justifies the model choice |
| **ANN training curves** | `ml/reports/ann_training_curves.png` | Accuracy/loss vs epoch, train vs validation — shows learning AND any overfitting honestly |
| **Elbow method + silhouette score** | `ml/reports/elbow_method.png` | Justifies K=3 for K-Means instead of just asserting it |
| **Cluster scatter plot (PCA)** | `ml/reports/cluster_scatter.png` | Visualizes the 3 clusters in 2D |
| **Per-student explainability** | `ml/app.py` → `explain_prediction()`, shown on the Prediction page | Explains *why* a student got their prediction — the top 2–3 weak, influential features — not just the number |
| **Prediction history & trend chart** | `frontend/student_detail.html` | Line chart of a student's Poor-risk probability over multiple predictions |
| **Bulk CSV upload** | `frontend/bulk_upload.html` | Add an entire class at once instead of one student at a time |
| **Print / Save as PDF** | Button on the Prediction page | Clean printable report per student via the browser's print dialog |
| **Local Chart.js + PapaParse** | `frontend/js/lib/` | Bundled directly in the project — no CDN/internet dependency for charts or CSV parsing, so the app works fully offline on any network |

The dataset generator was also updated to include realistic class overlap
and ~4% label noise, so the model's accuracy is a defensible ~93–97%
instead of a suspicious 100% — and the confusion matrix has genuine
(if few) misclassifications to discuss in your viva.

**If you already imported the database before this update**, run
`database/migration_add_explanations.sql` in phpMyAdmin's SQL tab to add
the new column without losing your existing data. New installs can just
import `database/student_ml_db.sql` as normal.

---

## 1.6 Round 2 of enhancements

A further batch of features was added on top of the ones above:

| Feature | Where | Why it matters |
|---|---|---|
| **Hyperparameter tuning (GridSearchCV)** | `ml/train_supervised.py` | Random Forest's `n_estimators`/`max_depth`/`min_samples_split` are now found by cross-validated grid search instead of hand-picked — real, defensible optimization. Results in `reports/gridsearch_results.csv` |
| **Model versioning** | `ml/models/versions/` | Every time you retrain, a timestamped copy is kept (never silently overwritten) with a `version_log.csv` tracking accuracy over time — lets you roll back if a retrain performs worse |
| **Correlation heatmap + feature distributions** | `ml/generate_eda.py` → `reports/correlation_heatmap.png`, `reports/feature_distributions.png` | Exploratory Data Analysis — shows which features move together and how each differs across Good/Average/Poor students. Good "Data Understanding" material for your report |
| **What-If Simulator** | `frontend/whatif.html` + `backend/simulate.php` | Drag sliders for attendance/marks/etc. and see the prediction update live — nothing is saved to any student record. Great live-demo tool for a viva |
| **Section/Department Comparison** | `frontend/section_comparison.html` + `backend/get_section_comparison.php` | Compares average risk and performance across different departments/sections side by side |
| **Duplicate roll-number detection** | `backend/add_student.php` | Adding a student with an already-used roll number now gives a clear "already exists" error instead of a raw database failure — Bulk Upload also surfaces this per-row |
| **API request logging** | `ml/app.py` → `ml/logs/predictions.log` | Every `/predict` call is logged with its input, prediction, and risk — an audit trail useful for debugging |
| **Automated tests** | `ml/tests/test_preprocessing.py` | 7 `pytest` tests covering the core preprocessing pipeline (feature order, scaling correctness, missing-field handling) — run with `python -m pytest tests/ -v` |
| **Dark mode toggle** | Sidebar on every page | Preference is saved in the browser (`localStorage`) and persists across pages/sessions |

**New sidebar links:** "What-If Simulator" and "Section Comparison" now appear alongside the existing pages.

**New Python packages needed:** `seaborn` (for the correlation heatmap) and `pytest` (for the tests):
```powershell
C:\mlenv\Scripts\python.exe -m pip install seaborn pytest
```

**To see the EDA report images**, run (from `ml/`):
```powershell
C:\mlenv\Scripts\python.exe generate_eda.py
```

**To run the automated tests** (from `ml/`):
```powershell
C:\mlenv\Scripts\python.exe -m pytest tests/ -v
```
All 7 should show `PASSED`.

### What was intentionally left out of this round

To avoid risking your already-working, hard-won setup, a few ambitious ideas from the brainstorm were **not** implemented:
- **Full role-based student self-service login** (students logging in to see only their own data) — this needs a real link between `users` and `students` tables and separate page-level access control; a solid version deserves its own focused pass rather than being bolted on quickly.
- **Real email/SMTP alerts** — would require a working mail server configuration on your machine, which is a common source of setup pain; the "Notify" concept can be revisited as a UI-only preview if you want it later.
- **Docker packaging** — not useful for a WAMP-based Windows setup like yours.

If any of these become priorities later (e.g., before a final submission or demo), they can be added as a focused follow-up.

---

## 2. Prerequisites

- **WAMP Server** (Windows, Apache, MySQL, PHP) — https://www.wampserver.com/
- **Python 3.9+** with pip
- A modern browser

---

## 3. Step-by-step setup (Windows + WAMP)

### Step A — Place the project inside WAMP's www folder
Copy the ENTIRE `Student-Performance-ML` folder into:
```
C:\wamp64\www\Student-Performance-ML\
```
Frontend and backend must live under the same WAMP site so that PHP session
cookies work correctly in the browser (same-origin).

### Step B — Import the database
1. Start WAMP (icon turns green).
2. Open `http://localhost/phpmyadmin`.
3. Click **Import** → choose `database/student_ml_db.sql` → click **Go**.
   This creates the `student_ml_db` database, all 5 tables, a default
   admin login, and 3 sample students.
4. Default login: **username `admin`, password `admin123`**.
   (The password is stored as a bcrypt hash — never as plain text.)

If your MySQL root user has a password, edit `backend/config.php`:
```php
define('DB_PASS', 'your_mysql_password');
```

### Step C — Set up the Python ML environment
Open a terminal in the `ml/` folder:
```bash
cd C:\wamp64\www\Student-Performance-ML\ml
pip install pandas numpy scikit-learn tensorflow flask joblib matplotlib
```
(`matplotlib` is new — it's used to save the confusion matrix, training
curves, elbow method, and cluster scatter plot images into `ml/reports/`.)

### Step D — Generate the dataset and train all 3 models
Run these **in order** (each one prints its own accuracy/summary so you can
see what's happening — good material for your viva):
```bash
python generate_dataset.py     # creates dataset/student_data.csv (~600 synthetic records)
python train_supervised.py     # Random Forest + cross-val + confusion matrix + model comparison
python train_ann.py            # ANN + training curve plots
python train_clustering.py     # K-Means + elbow method + silhouette score + cluster scatter plot
```
Each script now also saves evidence images/CSVs into `ml/reports/` —
open that folder afterward and you'll find:
```
reports/
├── confusion_matrix_rf.png     Where the Random Forest gets confused
├── feature_importance.png      Which inputs matter most
├── model_comparison.png/.csv   Random Forest vs Logistic Regression vs SVM
├── ann_training_curves.png     ANN accuracy/loss, train vs validation
├── elbow_method.png            Why K=3 was chosen for K-Means
└── cluster_scatter.png         2D visualization of the 3 clusters
```
Drop these images straight into your project report/slides as evidence.

(This repository already ships with trained model files in `ml/models/`
and pre-generated reports in `ml/reports/`, so the app works out of the
box — but re-running these scripts regenerates everything from scratch,
which is useful to show live during your demo.)

### Step E — Start the Flask ML API
Still inside `ml/`:
```bash
python app.py
```
You should see `All models loaded successfully.` and Flask listening on
`http://127.0.0.1:5000`. **Leave this terminal window open** — the PHP
backend calls this API every time a teacher clicks "Predict Performance".

Quick test in a browser: `http://127.0.0.1:5000/health` → `{"status":"ok",...}`

### Step F — Open the app
Go to:
```
http://localhost/Student-Performance-ML/frontend/login.html
```
Log in with `admin` / `admin123`.

---

## 4. Using the app

1. **Dashboard** — total students, performance distribution chart, cluster
   distribution chart, at-risk student list.
2. **Add Student** — create a profile, then immediately enter their
   attendance/marks/study hours etc.
3. **Predict Performance** — pick a student, click **Predict Performance**.
   This sends the student's saved academic data through:
   `JS → predict.php (PHP) → Flask /predict (Python) → Random Forest + ANN
   + K-Means → risk rule → recommendations → back to PHP → saved in MySQL
   → shown on screen` (including a risk gauge, probability bars, model
   comparison table, cluster name, and recommendations).
4. **Students** — search, view latest prediction/risk/cluster, delete.
5. **Analytics** — risk-level pie chart, cluster bar chart, full at-risk table.

---

## 5. How PHP and Python talk to each other

```
Browser (JS fetch)
     ↓
predict.php (PHP)
     ↓  reads latest academic data for the student from MySQL
     ↓  sends 8 features as JSON via cURL
Flask /predict (Python)
     ↓  scales features with the SAME scaler used in training
     ↓  Random Forest.predict_proba()
     ↓  ANN.predict()
     ↓  K-Means.predict() + cluster name lookup
     ↓  applies project-defined risk rule
     ↓  builds recommendation list
     ↓  returns one JSON object
predict.php (PHP)
     ↓  stores prediction + cluster in MySQL (prepared statements)
     ↓  returns JSON to the browser
Browser renders the result
```

`ML_API_URL` in `backend/config.php` points to `http://127.0.0.1:5000/predict`.
Change this if you run Flask on a different host/port.

---

## 6. Risk rule (project-defined, not medical/scientific)

```
Poor-probability ≥ 60%  → HIGH risk
Poor-probability 30–59% → MEDIUM risk
Poor-probability < 30%  → LOW risk
```
Defined in `ml/app.py` → `calculate_risk()`. Document this clearly in your
report/viva as a rule YOU chose for this project, not an external standard.

---

## 7. Database schema summary

| Table | Purpose |
|---|---|
| `users` | Login credentials (bcrypt-hashed passwords) |
| `students` | Roll number, name, email, department, year, section |
| `student_performance` | Attendance, marks, study hours, etc. (one row per data entry) |
| `predictions` | Random Forest + ANN + combined result, probabilities, risk, recommendations |
| `clusters` | K-Means cluster number + friendly name per prediction run |

Full DDL in `database/student_ml_db.sql`.

---

## 8. Testing checklist

- [ ] `http://127.0.0.1:5000/health` returns `{"status":"ok"}`
- [ ] Login page rejects wrong password, accepts `admin`/`admin123`
- [ ] Add Student → Save → Academic Data form unlocks
- [ ] Predict Performance → gauge, probabilities, cluster, recommendations all appear
- [ ] Dashboard totals update after a new prediction
- [ ] Students page search + delete work
- [ ] Stopping `python app.py` and clicking Predict shows a clear
      "Could not reach ML API" error (proves the PHP↔Flask bridge is real,
      not hard-coded)

---

## 9. Explaining each ML concept in your viva

**Supervised Learning:** "We use labeled historical student data where the
final performance category is known. The Random Forest model learns the
relationship between academic features and performance, then predicts the
category for new students."

**ANN:** "We use an Artificial Neural Network with three hidden Dense layers
(64→32→16 neurons, ReLU) and a softmax output layer to learn nonlinear
relationships between features and predict Good/Average/Poor probabilities."

**Unsupervised Learning:** "We use K-Means clustering because student groups
aren't predefined — the algorithm groups students purely by feature
similarity. We then inspect each cluster's average attendance/marks to
assign human-readable labels (High Performer / Average Performer /
At-Risk Student)."

**At-Risk Detection:** "The combined Poor-probability from Random Forest and
ANN is compared against project-defined thresholds (60% / 30%) to classify
risk as Low, Medium, or High."

---

## 10. Notes & limitations

- The shipped dataset is **synthetically generated** for academic
  demonstration (`ml/generate_dataset.py`) — clearly say this in your
  report. Swap in real (anonymized) student records for a stronger result.
- CNN was intentionally **not** included — it's designed for image data,
  and this project's data is tabular. Supervised + ANN + Unsupervised is a
  complete, defensible ML story for structured student data.
- This is a learning/demo project: for real deployment, add HTTPS, rate
  limiting on the Flask API, stronger session security, and input
  validation hardening.
