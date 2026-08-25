<?php
/**
 * save_performance.php
 * Saves a student's academic/behavioral input data into MySQL.
 * Expects POST JSON:
 * {
 *   student_id, attendance, assignment_score, internal_marks,
 *   previous_semester_marks, study_hours, quiz_score,
 *   participation, assignment_completion
 * }
 */
require_once 'config.php';
require_login();

$input = json_decode(file_get_contents('php://input'), true);

$student_id = intval($input['student_id'] ?? 0);
$fields = ['attendance', 'assignment_score', 'internal_marks', 'previous_semester_marks',
           'study_hours', 'quiz_score', 'participation', 'assignment_completion'];

if ($student_id <= 0) {
    send_json(['error' => 'Valid student_id is required.'], 400);
}

$values = [];
foreach ($fields as $f) {
    if (!isset($input[$f]) || !is_numeric($input[$f])) {
        send_json(['error' => "Field '$f' must be a numeric value."], 400);
    }
    $values[$f] = floatval($input[$f]);
}

$stmt = $conn->prepare(
    "INSERT INTO student_performance
    (student_id, attendance, assignment_score, internal_marks, previous_semester_marks,
     study_hours, quiz_score, participation, assignment_completion)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
);
$stmt->bind_param(
    'idddddddd',
    $student_id,
    $values['attendance'], $values['assignment_score'], $values['internal_marks'],
    $values['previous_semester_marks'], $values['study_hours'], $values['quiz_score'],
    $values['participation'], $values['assignment_completion']
);

if ($stmt->execute()) {
    send_json(['message' => 'Performance data saved successfully', 'performance_id' => $stmt->insert_id]);
} else {
    send_json(['error' => 'Failed to save performance data: ' . $stmt->error], 500);
}
