<?php
/**
 * predict.php
 * THE core bridge between PHP and the Python Flask ML API.
 *
 * Flow:
 *   1. Receive student_id (+ optionally raw feature values) from the frontend
 *   2. Fetch the student's LATEST performance record from MySQL (if not
 *      supplied directly)
 *   3. Send those 8 features as JSON to the Flask ML API (predict.php -> Flask)
 *   4. Flask returns Random Forest + ANN + K-Means + risk + recommendations
 *   5. Store the prediction & cluster result back into MySQL
 *   6. Return the full JSON result to the frontend
 *
 * Expects POST JSON: { "student_id": 101 }
 * (Optionally the 8 raw features can be sent instead of student_id alone,
 *  in which case they override the DB values.)
 */
require_once 'config.php';
require_login();

$input = json_decode(file_get_contents('php://input'), true);
$student_id = intval($input['student_id'] ?? 0);

if ($student_id <= 0) {
    send_json(['error' => 'Valid student_id is required.'], 400);
}

$feature_fields = ['attendance', 'assignment_score', 'internal_marks', 'previous_semester_marks',
                    'study_hours', 'quiz_score', 'participation', 'assignment_completion'];

// ---- Step 1: get the latest performance record for this student ----
$stmt = $conn->prepare(
    "SELECT * FROM student_performance WHERE student_id = ? ORDER BY performance_id DESC LIMIT 1"
);
$stmt->bind_param('i', $student_id);
$stmt->execute();
$perf = $stmt->get_result()->fetch_assoc();

if (!$perf) {
    send_json(['error' => 'No performance data found for this student. Please enter academic data first.'], 404);
}

// Allow the request body to override values (e.g. "what-if" prediction from the form)
$features = [];
foreach ($feature_fields as $f) {
    $features[$f] = isset($input[$f]) && is_numeric($input[$f]) ? floatval($input[$f]) : floatval($perf[$f]);
}

// ---- Step 2: call the Flask ML API ----
$ch = curl_init(ML_API_URL);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($features));
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 15);

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$curl_error = curl_error($ch);
curl_close($ch);

if ($response === false) {
    send_json(['error' => 'Could not reach ML API. Is Flask running (python app.py)? Details: ' . $curl_error], 502);
}

$ml_result = json_decode($response, true);

if ($http_code !== 200 || !$ml_result || isset($ml_result['error'])) {
    send_json(['error' => 'ML API error: ' . ($ml_result['error'] ?? 'Unknown error')], 502);
}

// ---- Step 3: store prediction in MySQL ----
$recommendations_str = implode('; ', $ml_result['recommendations']);
$explanations_str = implode('; ', $ml_result['explanations'] ?? []);

$stmt = $conn->prepare(
    "INSERT INTO predictions
    (student_id, supervised_prediction, ann_prediction, final_prediction,
     good_probability, average_probability, poor_probability, risk_level,
     cluster_name, recommendations, explanations)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
);
$stmt->bind_param(
    'isssdddssss',
    $student_id,
    $ml_result['supervised_prediction'],
    $ml_result['ann_prediction'],
    $ml_result['final_prediction'],
    $ml_result['good_probability'],
    $ml_result['average_probability'],
    $ml_result['poor_probability'],
    $ml_result['risk_level'],
    $ml_result['cluster_name'],
    $recommendations_str,
    $explanations_str
);
$stmt->execute();

// ---- Step 4: store cluster assignment ----
$stmt2 = $conn->prepare(
    "INSERT INTO clusters (student_id, cluster_number, cluster_name) VALUES (?, ?, ?)"
);
$stmt2->bind_param('iis', $student_id, $ml_result['cluster_id'], $ml_result['cluster_name']);
$stmt2->execute();

// ---- Step 5: get student name for a friendlier response ----
$stmt3 = $conn->prepare("SELECT name, roll_number FROM students WHERE student_id = ?");
$stmt3->bind_param('i', $student_id);
$stmt3->execute();
$student = $stmt3->get_result()->fetch_assoc();

$ml_result['student_id'] = $student_id;
$ml_result['student_name'] = $student['name'] ?? null;
$ml_result['roll_number'] = $student['roll_number'] ?? null;

send_json($ml_result);
