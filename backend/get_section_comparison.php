<?php
/**
 * get_section_comparison.php
 * Aggregates the LATEST prediction per student, grouped by
 * department + section, so a teacher can compare how different
 * classes/sections are doing against each other.
 *
 * GET get_section_comparison.php
 */
require_once 'config.php';
require_login();

$sql = "
    SELECT
        s.department, s.section,
        COUNT(*) AS total_students,
        SUM(CASE WHEN pr.final_prediction = 'Good' THEN 1 ELSE 0 END) AS good_count,
        SUM(CASE WHEN pr.final_prediction = 'Average' THEN 1 ELSE 0 END) AS average_count,
        SUM(CASE WHEN pr.final_prediction = 'Poor' THEN 1 ELSE 0 END) AS poor_count,
        SUM(CASE WHEN pr.risk_level = 'HIGH' THEN 1 ELSE 0 END) AS high_risk_count,
        SUM(CASE WHEN pr.risk_level = 'MEDIUM' THEN 1 ELSE 0 END) AS medium_risk_count,
        ROUND(AVG(p.attendance), 1) AS avg_attendance,
        ROUND(AVG(pr.poor_probability), 1) AS avg_poor_probability
    FROM students s
    LEFT JOIN (
        SELECT pr1.* FROM predictions pr1
        INNER JOIN (
            SELECT student_id, MAX(prediction_id) AS max_id
            FROM predictions GROUP BY student_id
        ) latest ON pr1.prediction_id = latest.max_id
    ) pr ON pr.student_id = s.student_id
    LEFT JOIN (
        SELECT sp1.* FROM student_performance sp1
        INNER JOIN (
            SELECT student_id, MAX(performance_id) AS max_id
            FROM student_performance GROUP BY student_id
        ) latest ON sp1.performance_id = latest.max_id
    ) p ON p.student_id = s.student_id
    GROUP BY s.department, s.section
    ORDER BY s.department, s.section
";

$result = $conn->query($sql);
if (!$result) {
    send_json(['error' => 'Query failed: ' . $conn->error], 500);
}

$sections = [];
while ($row = $result->fetch_assoc()) {
    // Only include sections that have at least one prediction on record
    $row['total_students'] = (int)$row['total_students'];
    $row['good_count'] = (int)$row['good_count'];
    $row['average_count'] = (int)$row['average_count'];
    $row['poor_count'] = (int)$row['poor_count'];
    $row['high_risk_count'] = (int)$row['high_risk_count'];
    $row['medium_risk_count'] = (int)$row['medium_risk_count'];
    $sections[] = $row;
}

send_json(['sections' => $sections]);
