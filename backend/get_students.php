<?php
/**
 * get_students.php
 * Returns all students, optionally with their latest performance record,
 * latest prediction and latest cluster - used by dashboard/students page.
 * GET /get_students.php            -> all students
 * GET /get_students.php?search=xyz -> filter by name or roll number
 */
require_once 'config.php';
require_login();

$search = trim($_GET['search'] ?? '');

$sql = "
    SELECT
        s.student_id, s.roll_number, s.name, s.email, s.department, s.year, s.section,
        p.attendance, p.assignment_score, p.internal_marks, p.previous_semester_marks,
        p.study_hours, p.quiz_score, p.participation, p.assignment_completion,
        pr.final_prediction, pr.risk_level, pr.good_probability, pr.average_probability,
        pr.poor_probability, pr.prediction_date,
        c.cluster_name
    FROM students s
    LEFT JOIN (
        SELECT sp1.* FROM student_performance sp1
        INNER JOIN (
            SELECT student_id, MAX(performance_id) AS max_id
            FROM student_performance GROUP BY student_id
        ) latest ON sp1.performance_id = latest.max_id
    ) p ON p.student_id = s.student_id
    LEFT JOIN (
        SELECT pr1.* FROM predictions pr1
        INNER JOIN (
            SELECT student_id, MAX(prediction_id) AS max_id
            FROM predictions GROUP BY student_id
        ) latest ON pr1.prediction_id = latest.max_id
    ) pr ON pr.student_id = s.student_id
    LEFT JOIN (
        SELECT c1.* FROM clusters c1
        INNER JOIN (
            SELECT student_id, MAX(cluster_id) AS max_id
            FROM clusters GROUP BY student_id
        ) latest ON c1.cluster_id = latest.max_id
    ) c ON c.student_id = s.student_id
";

if ($search !== '') {
    $sql .= " WHERE s.name LIKE ? OR s.roll_number LIKE ? ";
    $stmt = $conn->prepare($sql . " ORDER BY s.student_id DESC");
    $like = "%$search%";
    $stmt->bind_param('ss', $like, $like);
    $stmt->execute();
    $result = $stmt->get_result();
} else {
    $sql .= " ORDER BY s.student_id DESC";
    $result = $conn->query($sql);
}

$students = [];
while ($row = $result->fetch_assoc()) {
    $students[] = $row;
}

send_json(['students' => $students]);
