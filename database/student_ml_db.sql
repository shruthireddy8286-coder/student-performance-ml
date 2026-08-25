-- ============================================================
-- student_ml_db.sql
-- Database schema for AI-Based Student Performance Prediction,
-- Student Segmentation and At-Risk Student Detection project.
--
-- HOW TO USE (Windows + WAMP):
--   1. Start WAMP, click the WAMP icon -> phpMyAdmin
--      (or open http://localhost/phpmyadmin)
--   2. Click "Import" tab
--   3. Choose this file (student_ml_db.sql) and click "Go"
--   This will create the database + tables + sample data automatically.
-- ============================================================

CREATE DATABASE IF NOT EXISTS student_ml_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE student_ml_db;

-- ------------------------------------------------------------
-- 1. users  (login / authentication)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,   -- stores a bcrypt HASH, never plain text
    role VARCHAR(20) NOT NULL DEFAULT 'teacher',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Default admin login: username = admin / password = admin123
-- The hash below was generated with PHP's password_hash() (bcrypt).
-- IMPORTANT: change this password after first login in a real deployment.
INSERT INTO users (username, password, role) VALUES
('admin', '$2b$10$cjN/upxA19eclh4VoiKn/et3Cqb1vbTMaicfA4hZVKa2o0QelyGwO', 'admin')
ON DUPLICATE KEY UPDATE username = username;

-- ------------------------------------------------------------
-- 2. students  (basic student profile)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    roll_number VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    department VARCHAR(50),
    year INT,
    section VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- 3. student_performance  (academic + behavioral inputs)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS student_performance (
    performance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    attendance DECIMAL(5,2) NOT NULL,
    assignment_score DECIMAL(5,2) NOT NULL,
    internal_marks DECIMAL(5,2) NOT NULL,
    previous_semester_marks DECIMAL(5,2) NOT NULL,
    study_hours DECIMAL(4,2) NOT NULL,
    quiz_score DECIMAL(5,2) NOT NULL,
    participation DECIMAL(5,2) NOT NULL,
    assignment_completion DECIMAL(5,2) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 4. predictions  (model outputs)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    supervised_prediction VARCHAR(20),
    ann_prediction VARCHAR(20),
    final_prediction VARCHAR(20),
    good_probability DECIMAL(5,2),
    average_probability DECIMAL(5,2),
    poor_probability DECIMAL(5,2),
    risk_level VARCHAR(10),
    cluster_name VARCHAR(30),
    recommendations TEXT,
    explanations TEXT,
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 5. clusters  (latest cluster assignment per student)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clusters (
    cluster_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    cluster_number INT NOT NULL,
    cluster_name VARCHAR(30) NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- Sample students (so the dashboard isn't empty on first run)
-- ------------------------------------------------------------
INSERT INTO students (roll_number, name, email, department, year, section) VALUES
('101', 'Rahul Sharma', 'rahul@example.com', 'CSE', 3, 'A'),
('118', 'Priya Verma', 'priya@example.com', 'CSE', 3, 'B'),
('135', 'Arjun Rao', 'arjun@example.com', 'ECE', 2, 'A');

INSERT INTO student_performance
(student_id, attendance, assignment_score, internal_marks, previous_semester_marks, study_hours, quiz_score, participation, assignment_completion)
VALUES
(1, 68, 55, 58, 61, 1.5, 52, 50, 60),
(2, 95, 90, 88, 85, 5, 92, 90, 100),
(3, 78, 72, 70, 74, 2.5, 68, 65, 75);
