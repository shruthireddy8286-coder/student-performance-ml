<?php
/**
 * update_student.php
 * Updates an existing student's profile fields.
 * Expects POST JSON: { student_id, roll_number, name, email, department, year, section }
 */
require_once 'config.php';
require_login();

$input = json_decode(file_get_contents('php://input'), true);

$student_id  = intval($input['student_id'] ?? 0);
$roll_number = trim($input['roll_number'] ?? '');
$name        = trim($input['name'] ?? '');
$email       = trim($input['email'] ?? '');
$department  = trim($input['department'] ?? '');
$year        = intval($input['year'] ?? 0);
$section     = trim($input['section'] ?? '');

if ($student_id <= 0 || $name === '') {
    send_json(['error' => 'student_id and name are required.'], 400);
}

$stmt = $conn->prepare(
    "UPDATE students
     SET roll_number = ?, name = ?, email = ?, department = ?, year = ?, section = ?
     WHERE student_id = ?"
);
$stmt->bind_param('ssssisi', $roll_number, $name, $email, $department, $year, $section, $student_id);

if ($stmt->execute()) {
    send_json(['message' => 'Student updated successfully']);
} else {
    send_json(['error' => 'Failed to update student: ' . $stmt->error], 500);
}
