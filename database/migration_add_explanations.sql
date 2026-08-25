-- ============================================================
-- migration_add_explanations.sql
--
-- Run this ONLY if you already imported student_ml_db.sql before
-- and don't want to re-import from scratch (which would wipe your
-- existing student/prediction data).
--
-- This just adds the new `explanations` column used by the
-- per-student explainability feature.
--
-- HOW TO USE:
--   phpMyAdmin -> select your database -> SQL tab -> paste this in -> Go
-- ============================================================

ALTER TABLE predictions
    ADD COLUMN IF NOT EXISTS explanations TEXT AFTER recommendations;
