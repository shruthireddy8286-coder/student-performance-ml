<?php
/**
 * config.php
 * Central database connection + shared settings for the whole backend.
 * Every other PHP file includes this first.
 */

// ---- MySQL connection settings (WAMP defaults) ----
define('DB_HOST', 'localhost');
define('DB_USER', 'root');
define('DB_PASS', '');           // default WAMP root password is empty
define('DB_NAME', 'student performance-ml');

// ---- Python Flask ML API URL ----
define('ML_API_URL', 'http://127.0.0.1:5000/predict');

// ---- Start session for login state ----
if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

// ---- Create a single reusable MySQLi connection ----
$conn = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);

if ($conn->connect_error) {
    http_response_code(500);
    die(json_encode(['error' => 'Database connection failed: ' . $conn->connect_error]));
}

$conn->set_charset('utf8mb4');

/**
 * Helper: send a JSON response and stop execution.
 */
function send_json($data, $status_code = 200) {
    http_response_code($status_code);
    header('Content-Type: application/json');
    echo json_encode($data);
    exit;
}

/**
 * Helper: require the user to be logged in before continuing.
 * Any backend endpoint that touches student data should call this.
 */
function require_login() {
    if (!isset($_SESSION['user_id'])) {
        send_json(['error' => 'Not authenticated. Please log in.'], 401);
    }
}
