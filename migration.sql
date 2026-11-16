-- BACK UP the gym database before running this migration.
-- Adds ownership fields without deleting existing workout/cardio records.
ALTER TABLE workouts ADD COLUMN user_id INT NULL AFTER sno;
ALTER TABLE cardio ADD COLUMN user_id INT NULL AFTER sno;
-- Pending=0, Approved=1, Rejected=2. Existing approved=0 rows remain pending.
ALTER TABLE attendance MODIFY admin_id INT NULL;
ALTER TABLE attendance MODIFY approved TINYINT(1) NOT NULL DEFAULT 0;
-- Ensure date columns are real datetime values as expected by the updated Flask models.
ALTER TABLE workouts MODIFY date DATETIME(6) NOT NULL;
ALTER TABLE cardio MODIFY date DATETIME(6) NOT NULL;
-- Account timestamps should be DATETIME, not VARCHAR.
ALTER TABLE account MODIFY created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP;
