<?php
/**
 * simulate.php
 * Powers the "What-If Simulator" page. Unlike predict.php, this does
 * NOT read from or write to MySQL — it takes raw feature values
 * straight from the frontend sliders and forwards them directly to
 * the Flask ML API, purely for exploration ("what if this student's
 * attendance were 90% instead of 60%?"). Nothing is saved.
 *
 * Expects POST JSON with all 8 raw feature values:
 * { attendance, assignment_score, internal_marks, previous_semester_marks,
 *   study_hours, quiz_score, participation, assignment_completion }
 */
require_once 'config.php';
require_login();

$input = json_decode(file_get_contents('php://input'), true);

$feature_fields = ['attendance', 'assignment_score', 'internal_marks', 'previous_semester_marks',
                    'study_hours', 'quiz_score', 'participation', 'assignment_completion'];

$features = [];
foreach ($feature_fields as $f) {
    if (!isset($input[$f]) || !is_numeric($input[$f])) {
        send_json(['error' => "Field '$f' must be a numeric value."], 400);
    }
    $features[$f] = floatval($input[$f]);
}

// ---- Call the Flask ML API directly (no DB read/write) ----
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

// Nothing is stored — this is a pure simulation.
send_json($ml_result);
