<?php
/**
 * add_student.php
 * Adds a new student profile.
 * Expects POST JSON: { roll_number, name, email, department, year, section }
 */
require_once 'config.php';
require_login();

$input = json_decode(file_get_contents('php://input'), true);

$roll_number = trim($input['roll_number'] ?? '');
$name        = trim($input['name'] ?? '');
$email       = trim($input['email'] ?? '');
$department  = trim($input['department'] ?? '');
$year        = intval($input['year'] ?? 0);
$section     = trim($input['section'] ?? '');

if ($roll_number === '' || $name === '') {
    send_json(['error' => 'Roll number and name are required.'], 400);
}

// ---- Duplicate check: give a clear, specific error instead of a raw SQL failure ----
$check = $conn->prepare("SELECT student_id FROM students WHERE roll_number = ? LIMIT 1");
$check->bind_param('s', $roll_number);
$check->execute();
if ($check->get_result()->num_rows > 0) {
    send_json(['error' => "Roll number '$roll_number' already exists for another student."], 409);
}

$stmt = $conn->prepare(
    "INSERT INTO students (roll_number, name, email, department, year, section)
     VALUES (?, ?, ?, ?, ?, ?)"
);
$stmt->bind_param('ssssis', $roll_number, $name, $email, $department, $year, $section);

if ($stmt->execute()) {
    send_json(['message' => 'Student added successfully', 'student_id' => $stmt->insert_id]);
} else {
    send_json(['error' => 'Failed to add student: ' . $stmt->error], 500);
}
