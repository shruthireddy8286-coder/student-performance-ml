<?php
/**
 * login.php
 * Authenticates a teacher/admin using a hashed password stored in MySQL.
 * Expects POST JSON: { "username": "...", "password": "..." }
 */
require_once 'config.php';

$input = json_decode(file_get_contents('php://input'), true);

$username = trim($input['username'] ?? '');
$password = $input['password'] ?? '';

if ($username === '' || $password === '') {
    send_json(['error' => 'Username and password are required.'], 400);
}

// Use a PREPARED STATEMENT to prevent SQL injection
$stmt = $conn->prepare("SELECT id, username, password, role FROM users WHERE username = ? LIMIT 1");
$stmt->bind_param('s', $username);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows === 0) {
    send_json(['error' => 'Invalid username or password.'], 401);
}

$user = $result->fetch_assoc();

// Verify against the bcrypt hash stored in the database
if (!password_verify($password, $user['password'])) {
    send_json(['error' => 'Invalid username or password.'], 401);
}

$_SESSION['user_id'] = $user['id'];
$_SESSION['username'] = $user['username'];
$_SESSION['role'] = $user['role'];

send_json([
    'message' => 'Login successful',
    'username' => $user['username'],
    'role' => $user['role'],
]);
