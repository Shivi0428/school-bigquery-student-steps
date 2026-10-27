# School analytics on BigQuery

I built this as a small, friendly project for anyone learning Google Cloud's BigQuery for the first time. The idea is simple: a school wants to know which students might need extra help. We make up the school data, load it into BigQuery, clean it with SQL, and ask the data who needs attention.

Everything is fake. No real student appears anywhere in this repo.

## Where this project stands

I want to be upfront about this:

- The data generator and its tests run on any computer, and they pass. GitHub checks them on every push.
- The BigQuery steps (loading the data and running the SQL) are written and reviewed, but I haven't run them against a live Google Cloud project yet. If you try them, please check the results and tell me what you find.

## What you'll do

1. Create a free Google Cloud project.
2. Make sure BigQuery is switched on.
3. Set up Python on your computer.
4. Generate the fake school data.
5. Run the tests.
6. Log in to Google Cloud from your computer.
7. Load the data into BigQuery.
8. Look at the cleaned-up views.
9. Look at the report tables.
10. Run the data checks.
11. Clean up, so nothing keeps costing money.

## A quick word about cost

BigQuery has a free tier of 1 TB of queries and 10 GB of storage each month. This project uses a few megabytes, so it should stay free. Still, set a budget alert for about £5 in Google Cloud Billing before you start. It takes a minute and gives you peace of mind. And do step 11 when you're done.

## Step 1: Create a project

1. Open <https://console.cloud.google.com>.
2. Click the project name at the top, then **New project**.
3. Call it something like `school-bigquery-yourname` and click **Create**.
4. Write down the **project ID**. It can be different from the name, and you'll need it in step 7.

## Step 2: Check BigQuery is on

Search for "BigQuery" in the console and open it. If you see an empty explorer panel on the left, you're ready.

## Step 3: Set up Python

You need Python 3.11 or newer. Make a virtual environment and install the packages:

```bash
python -m venv .venv
```

Activate it. On Windows:

```bash
.venv\Scripts\activate
```

On Mac or Linux:

```bash
source .venv/bin/activate
```

Then install:

```bash
pip install -r requirements.txt
```

## Step 4: Make the fake data

```bash
python scripts/generate_school_data.py
```

You'll get three files in `data/raw/`:

- `students.csv` has 120 students, each in a class and a section.
- `attendance.csv` has one row per student per school day.
- `marks.csv` has marks for 5 subjects across 3 terms.

The generator uses a fixed seed, so you get the same data every time. That makes it easy to compare your results with someone else's.

## Step 5: Run the tests

```bash
pytest -q
```

You should see `7 passed`. The tests check simple but important rules, like "every mark belongs to a real student" and "scores are between 0 and 100". You don't need a Google account for this step.

```bash
ruff check scripts tests
```

You should see `All checks passed!`.

## Step 6: Log in to Google Cloud

Install the Google Cloud CLI from <https://cloud.google.com/sdk/docs/install>, then run:

```bash
gcloud auth application-default login
```

```bash
gcloud config set project YOUR_PROJECT_ID
```

Swap in the project ID from step 1. Never paste passwords or keys into the code. This login keeps them safely out of the repo.

## Step 7: Load the data into BigQuery

```bash
python scripts/load_to_bigquery.py --project YOUR_PROJECT_ID --location EU
```

This does three things for you:

1. Creates two datasets: `school_raw` for the untouched data and `school_mart` for the reports.
2. Loads the three CSV files into `school_raw`.
3. Runs the SQL files in `sql/` in order and prints the check results.

Keeping raw data and reports apart is a good habit. If a report ever looks wrong, you can rebuild it from the raw data.

## Step 8: Look at the clean views

In the BigQuery console, try:

```sql
SELECT * FROM `YOUR_PROJECT_ID.school_mart.stg_students` LIMIT 10;
```

Tables starting with `stg_` are **views**. A view stores no data of its own. It's a saved question that BigQuery answers fresh each time.

## Step 9: Look at the report tables

Run these one at a time:

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

The `at_risk_students` table lists students whose attendance is under 75% or whose average mark is under 40. It's a starting point for a teacher's conversation, not a verdict on any child.

## Step 10: Run the checks

The loader prints the results of `sql/03_checks.sql`. Each check should show `problems: 0`. If one doesn't, work out why before you trust the report tables.

## Step 11: Clean up

Delete the datasets so nothing keeps costing money:

```bash
bq rm -r -f -d YOUR_PROJECT_ID:school_raw
```

```bash
bq rm -r -f -d YOUR_PROJECT_ID:school_mart
```

If you're done with the whole project, you can delete it from **IAM & Admin → Manage resources**.

## Why I made these choices

- **BigQuery** is serverless. There are no machines to look after, and you pay for what you scan.
- **Views and tables.** Views are cheap and always fresh. Tables are quicker when many people run the same report.
- **`WRITE_TRUNCATE` when loading.** Running the loader twice gives the same result, which makes it safe to retry.
- **Separate datasets.** Raw data stays untouched, and reports can always be rebuilt.
- **Tests and checks.** The pytest tests guard the generator, and the SQL checks guard the data in BigQuery.

## What's in the repo

```
scripts/generate_school_data.py   makes the fake CSV files
scripts/load_to_bigquery.py       loads the CSVs and runs the SQL
sql/01_staging.sql                the clean views
sql/02_marts.sql                  the report tables
sql/03_checks.sql                 the data checks
tests/                            tests for the generator (no Google account needed)
.github/workflows/ci.yml          runs lint and tests on every push
```

## A note on the data

All names, marks and attendance figures are randomly generated. The project is for learning, and it's free to use that way.
