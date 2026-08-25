<?php
/**
 * get_predictions.php
 * Returns prediction history — either for one student (?student_id=101)
 * or dashboard-wide aggregate stats (used by dashboard.html + Chart.js).
 *
 * GET get_predictions.php                -> dashboard summary + at-risk list
 * GET get_predictions.php?student_id=101 -> full prediction history for one student
 */
require_once 'config.php';
require_login();

$student_id = intval($_GET['student_id'] ?? 0);

if ($student_id > 0) {
    // ---- Single student's full prediction history ----
    $stmt = $conn->prepare(
        "SELECT p.*, s.name, s.roll_number
         FROM predictions p
         JOIN students s ON s.student_id = p.student_id
         WHERE p.student_id = ?
         ORDER BY p.prediction_date DESC"
    );
    $stmt->bind_param('i', $student_id);
    $stmt->execute();
    $result = $stmt->get_result();
    $history = [];
    while ($row = $result->fetch_assoc()) {
        $history[] = $row;
    }
    send_json(['history' => $history]);
}

// ---- Dashboard-wide summary ----
$total_students = $conn->query("SELECT COUNT(*) AS c FROM students")->fetch_assoc()['c'];

// latest prediction per student
$latest_sql = "
    SELECT pr.* FROM predictions pr
    INNER JOIN (
        SELECT student_id, MAX(prediction_id) AS max_id
        FROM predictions GROUP BY student_id
    ) latest ON pr.prediction_id = latest.max_id
";
$latest_result = $conn->query($latest_sql);

$counts = ['Good' => 0, 'Average' => 0, 'Poor' => 0];
$risk_counts = ['LOW' => 0, 'MEDIUM' => 0, 'HIGH' => 0];
$cluster_counts = ['High Performer' => 0, 'Average Performer' => 0, 'At-Risk Student' => 0];
$avg_attendance_sum = 0;
$avg_attendance_n = 0;

while ($row = $latest_result->fetch_assoc()) {
    if (isset($counts[$row['final_prediction']])) {
        $counts[$row['final_prediction']]++;
    }
    if (isset($risk_counts[$row['risk_level']])) {
        $risk_counts[$row['risk_level']]++;
    }
    if (isset($cluster_counts[$row['cluster_name']])) {
        $cluster_counts[$row['cluster_name']]++;
    }
}

// average attendance across latest performance records
$att_result = $conn->query("
    SELECT AVG(p.attendance) AS avg_attendance FROM student_performance p
    INNER JOIN (
        SELECT student_id, MAX(performance_id) AS max_id
        FROM student_performance GROUP BY student_id
    ) latest ON p.performance_id = latest.max_id
");
$avg_attendance = round($att_result->fetch_assoc()['avg_attendance'] ?? 0, 1);

// at-risk student list (HIGH + MEDIUM), most recent first
$at_risk_result = $conn->query("
    SELECT s.roll_number, s.name, pr.risk_level, pr.final_prediction, pr.prediction_date
    FROM predictions pr
    INNER JOIN (
        SELECT student_id, MAX(prediction_id) AS max_id
        FROM predictions GROUP BY student_id
    ) latest ON pr.prediction_id = latest.max_id
    JOIN students s ON s.student_id = pr.student_id
    WHERE pr.risk_level IN ('HIGH', 'MEDIUM')
    ORDER BY FIELD(pr.risk_level, 'HIGH', 'MEDIUM'), pr.prediction_date DESC
");
$at_risk_list = [];
while ($row = $at_risk_result->fetch_assoc()) {
    $at_risk_list[] = $row;
}

send_json([
    'total_students' => (int)$total_students,
    'performance_distribution' => $counts,
    'risk_distribution' => $risk_counts,
    'cluster_distribution' => $cluster_counts,
    'average_attendance' => $avg_attendance,
    'at_risk_students' => $at_risk_list,
]);
