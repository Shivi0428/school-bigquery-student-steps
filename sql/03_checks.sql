-- Step 3 of the SQL: quality checks. Each query should return 0 rows (or the number shown as 0).
-- The loader prints these results. Read them there or in the BigQuery console.

-- Check 1: every student id in the marks is a real student.
SELECT 'marks_without_student' AS check_name, COUNT(*) AS problems
FROM `{project}.{dataset}.stg_marks` m
LEFT JOIN `{project}.{dataset}.stg_students` s USING (student_id)
WHERE s.student_id IS NULL;

-- Check 2: attendance percentages are between 0 and 100.
SELECT 'attendance_out_of_range' AS check_name, COUNT(*) AS problems
FROM `{project}.{dataset}.student_attendance`
WHERE attendance_pct < 0 OR attendance_pct > 100;
