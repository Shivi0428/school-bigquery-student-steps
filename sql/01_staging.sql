-- Step 1 of the SQL: clean views on top of the raw tables.
-- Views cost nothing to store; BigQuery runs them when someone queries them.

CREATE OR REPLACE VIEW `{project}.{dataset}.stg_students` AS
SELECT
  student_id,
  TRIM(full_name)  AS full_name,
  class_name,
  section,
  ability
FROM `{project}.school_raw.students`;

CREATE OR REPLACE VIEW `{project}.{dataset}.stg_attendance` AS
SELECT
  student_id,
  school_date,
  present = 1 AS was_present
FROM `{project}.school_raw.attendance`;

CREATE OR REPLACE VIEW `{project}.{dataset}.stg_marks` AS
SELECT
  student_id,
  subject,
  term,
  score
FROM `{project}.school_raw.marks`
WHERE score BETWEEN 0 AND 100;
