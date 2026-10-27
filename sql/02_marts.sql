-- Step 2 of the SQL: report tables that students will query and chart.

-- Attendance percentage for each student over the whole period.
CREATE OR REPLACE TABLE `{project}.{dataset}.student_attendance` AS
SELECT
  s.student_id,
  s.full_name,
  s.class_name,
  COUNT(a.school_date)                                   AS school_days,
  COUNTIF(a.was_present)                                 AS days_present,
  ROUND(100 * COUNTIF(a.was_present) / COUNT(a.school_date), 1) AS attendance_pct
FROM `{project}.{dataset}.stg_students` AS s
LEFT JOIN `{project}.{dataset}.stg_attendance` AS a USING (student_id)
GROUP BY s.student_id, s.full_name, s.class_name;

-- Average score for each subject, class and term.
CREATE OR REPLACE TABLE `{project}.{dataset}.class_subject_scores` AS
SELECT
  s.class_name,
  m.subject,
  m.term,
  ROUND(AVG(m.score), 1) AS avg_score,
  COUNT(*)               AS marks_count
FROM `{project}.{dataset}.stg_marks` AS m
JOIN `{project}.{dataset}.stg_students` AS s USING (student_id)
GROUP BY s.class_name, m.subject, m.term;

-- Students who need a teacher's attention: low attendance OR low average marks.
CREATE OR REPLACE TABLE `{project}.{dataset}.at_risk_students` AS
WITH avg_marks AS (
  SELECT student_id, ROUND(AVG(score), 1) AS avg_score
  FROM `{project}.{dataset}.stg_marks`
  GROUP BY student_id
)
SELECT
  a.student_id,
  a.full_name,
  a.class_name,
  a.attendance_pct,
  m.avg_score,
  CASE
    WHEN a.attendance_pct < 75 AND m.avg_score < 40 THEN 'both'
    WHEN a.attendance_pct < 75 THEN 'attendance'
    WHEN m.avg_score < 40 THEN 'marks'
  END AS risk_reason
FROM `{project}.{dataset}.student_attendance` AS a
JOIN avg_marks AS m USING (student_id)
WHERE a.attendance_pct < 75 OR m.avg_score < 40;
