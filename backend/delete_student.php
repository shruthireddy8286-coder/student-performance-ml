<?php
/**
 * delete_student.php
 * Deletes a student and (via FOREIGN KEY ON DELETE CASCADE) their
 * performance records, predictions, and cluster history.
 * Expects POST JSON: { student_id }
 */
require_once 'config.php';
require_login();

$input = json_decode(file_get_contents('php://input'), true);
$student_id = intval($input['student_id'] ?? 0);

if ($student_id <= 0) {
    send_json(['error' => 'Valid student_id is required.'], 400);
}

$stmt = $conn->prepare("DELETE FROM students WHERE student_id = ?");
$stmt->bind_param('i', $student_id);

if ($stmt->execute()) {
    send_json(['message' => 'Student deleted successfully']);
} else {
    send_json(['error' => 'Failed to delete student: ' . $stmt->error], 500);
}
