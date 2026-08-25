<?php
/**
 * logout.php
 * Destroys the current session.
 */
require_once 'config.php';

$_SESSION = [];
session_destroy();

send_json(['message' => 'Logged out successfully']);
