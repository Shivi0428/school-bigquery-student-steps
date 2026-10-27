# School analytics on BigQuery: student steps

A step-by-step project for students learning **Google Cloud BigQuery**. You generate fake school data, load it into BigQuery, clean it with SQL, and find students who need help.

**Honest status:** The Python generator and its tests run on any computer, and they pass. The BigQuery steps have been written carefully but **not yet run against a real Google Cloud project** by the author. Run them yourself and check the results.

## What you will learn

| Step | Skill | Tool |
|---|---|---|
| 1 | Create a Google Cloud project | Console |
| 2 | Turn on BigQuery | Console |
| 3 | Set up Python on your computer | Terminal |
| 4 | Generate synthetic data | Python |
| 5 | Run the tests | pytest |
| 6 | Log in to Google Cloud from your computer | gcloud |
| 7 | Load CSV files into BigQuery | Python + BigQuery |
| 8 | Clean data with views | SQL |
| 9 | Build report tables | SQL |
| 10 | Check data quality | SQL |
| 11 | Clean up so you are not charged | Console |

## Before you start: cost

- BigQuery has a **free tier**: 1 TB of queries and 10 GB of storage each month.
- This project's data is small (a few MB), so it should cost nothing.
- **Set a budget alert** at £5 or $5 in Google Cloud Billing, so you are warned early.
- Delete the datasets when you finish (step 11).

## Step 1: Create a Google Cloud project

1. Go to <https://console.cloud.google.com>.
2. Click the project name at the top, then **New project**.
3. Name it `school-bigquery-<your-name>`, then click **Create**.
4. Note the **project ID** (it may differ from the name). You will need it in step 7.

## Step 2: Turn on BigQuery

BigQuery is usually on by default. To check, search for **BigQuery** in the console search bar and open it. You should see an empty explorer on the left.

## Step 3: Set up Python on your computer

You need Python 3.11 or newer.

```bash
python -m venv .venv
```

Activate it:

- Windows: `.venv\Scripts\activate`
- Mac or Linux: `source .venv/bin/activate`

Install the packages:

```bash
pip install -r requirements.txt
```

## Step 4: Generate synthetic data

```bash
python scripts/generate_school_data.py
```

This creates three files in `data/raw/`:

- `students.csv`: 120 students, with a class and a section.
- `attendance.csv`: one row per student per school day.
- `marks.csv`: marks for 5 subjects across 3 terms.

## Step 5: Run the tests

```bash
pytest -q
```

Expected: `7 passed`. The tests check the data rules, such as "every mark belongs to a real student" and "scores are between 0 and 100". No Google account is needed for this step.

```bash
ruff check scripts tests
```

Expected: `All checks passed!`

## Step 6: Log in to Google Cloud from your computer

Install the Google Cloud CLI (`gcloud`) from <https://cloud.google.com/sdk/docs/install>, then run:

```bash
gcloud auth application-default login
```

```bash
gcloud config set project YOUR_PROJECT_ID
```

Replace `YOUR_PROJECT_ID` with the ID from step 1.

## Step 7: Load the data into BigQuery

```bash
python scripts/load_to_bigquery.py --project YOUR_PROJECT_ID --location EU
```

What this does:

1. Creates two datasets: `school_raw` (raw data) and `school_mart` (report tables).
2. Loads the three CSV files into `school_raw`.
3. Runs every SQL file in `sql/` in order, and prints the check results.

## Step 8: Look at the clean views

Open BigQuery in the console and run:

```sql
SELECT * FROM `YOUR_PROJECT_ID.school_mart.stg_students` LIMIT 10;
```

`stg_` tables are **views**. They don't store data; they show the raw data in a cleaned form each time you query them.

## Step 9: Look at the report tables

Try these queries, one at a time:

```sql
SELECT class_name, subject, term, avg_score
FROM `YOUR_PROJECT_ID.school_mart.class_subject_scores`
ORDER BY avg_score DESC
LIMIT 10;
```

```sql
SELECT full_name, class_name, attendance_pct
FROM `YOUR_PROJECT_ID.school_mart.student_attendance`
ORDER BY attendance_pct ASC
LIMIT 10;
```

```sql
SELECT risk_reason, COUNT(*) AS students
FROM `YOUR_PROJECT_ID.school_mart.at_risk_students`
GROUP BY risk_reason;
```

## Step 10: Check data quality

The loader prints the results of `sql/03_checks.sql`. Each check should show `problems: 0`. If one doesn't, find out why before you trust the report tables.

## Step 11: Clean up

To stop any future charges, delete the datasets:

```bash
bq rm -r -f -d YOUR_PROJECT_ID:school_raw
```

```bash
bq rm -r -f -d YOUR_PROJECT_ID:school_mart
```

If you are finished with the whole project, delete it from **IAM & Admin → Manage resources**.

## What to explain in an interview

- **Why BigQuery?** It is serverless: you don't manage machines, and you pay for the data you scan.
- **Why views and tables?** Views are cheap and always fresh; tables are faster for repeated reports.
- **Why `WRITE_TRUNCATE`?** The loader replaces old data, so running it twice gives the same result. That's idempotent.
- **Why separate datasets?** Raw data and reports are kept apart, so a bad report can be rebuilt from raw data.
- **How do you know the data is right?** The checks in `sql/03_checks.sql`, and the tests in `tests/`.

## Project layout

```
scripts/generate_school_data.py   creates the synthetic CSV files
scripts/load_to_bigquery.py       loads CSVs and runs the SQL
sql/01_staging.sql                clean views
sql/02_marts.sql                  report tables
sql/03_checks.sql                 quality checks
tests/                            tests for the generator (no Google account needed)
.github/workflows/ci.yml          runs lint and tests on every push
```

## Licence

For learning. Data is synthetic; no real students are included.
