"""Load the CSV files into BigQuery, then run the SQL files in order.

Steps this script does:
  1. Create the dataset (school_raw / school_mart) if it does not exist.
  2. Load each CSV into a raw table, replacing the old table (WRITE_TRUNCATE).
  3. Run every .sql file in the sql/ folder, in name order, replacing {project} and {dataset}.

Before running, log in once on your computer:
  gcloud auth application-default login
  gcloud config set project YOUR_PROJECT_ID
"""

from __future__ import annotations

import argparse
from pathlib import Path

from google.cloud import bigquery

ROOT = Path(__file__).resolve().parents[1]
RAW_TABLES = {
    "students": "students.csv",
    "attendance": "attendance.csv",
    "marks": "marks.csv",
}
SCHEMAS = {
    "students": [
        bigquery.SchemaField("student_id", "INT64", mode="REQUIRED"),
        bigquery.SchemaField("full_name", "STRING"),
        bigquery.SchemaField("class_name", "STRING"),
        bigquery.SchemaField("section", "STRING"),
        bigquery.SchemaField("attendance_habit", "FLOAT64"),
        bigquery.SchemaField("ability", "FLOAT64"),
    ],
    "attendance": [
        bigquery.SchemaField("student_id", "INT64", mode="REQUIRED"),
        bigquery.SchemaField("school_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("present", "INT64"),
    ],
    "marks": [
        bigquery.SchemaField("student_id", "INT64", mode="REQUIRED"),
        bigquery.SchemaField("subject", "STRING"),
        bigquery.SchemaField("term", "INT64"),
        bigquery.SchemaField("score", "INT64"),
    ],
}


def load_raw(client: bigquery.Client, project: str, dataset: str, raw_dir: Path) -> None:
    for table, filename in RAW_TABLES.items():
        table_id = f"{project}.{dataset}.{table}"
        job_config = bigquery.LoadJobConfig(
            schema=SCHEMAS[table],
            skip_leading_rows=1,
            source_format=bigquery.SourceFormat.CSV,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )
        with (raw_dir / filename).open("rb") as fh:
            job = client.load_table_from_file(fh, table_id, job_config=job_config)
        job.result()  # wait until BigQuery finishes loading
        print(f"loaded {table_id}: {client.get_table(table_id).num_rows:,} rows")


def run_sql(client: bigquery.Client, project: str, dataset: str) -> None:
    for sql_file in sorted((ROOT / "sql").glob("*.sql")):
        text = sql_file.read_text(encoding="utf-8").replace("{project}", project).replace("{dataset}", dataset)
        for statement in [s.strip() for s in text.split(";") if s.strip()]:
            # Check queries return rows; CREATE statements return nothing.
            for row in client.query(statement).result():
                print(f"  check: {dict(row)}")
        print(f"ran {sql_file.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project", required=True, help="your GCP project id")
    parser.add_argument("--location", default="EU", help="BigQuery location (e.g. EU or US)")
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "data" / "raw")
    args = parser.parse_args()

    client = bigquery.Client(project=args.project, location=args.location)
    for dataset in ("school_raw", "school_mart"):
        client.create_dataset(bigquery.Dataset(f"{args.project}.{dataset}"), exists_ok=True)

    load_raw(client, args.project, "school_raw", args.raw_dir)
    run_sql(client, args.project, "school_mart")
    print("done. Open BigQuery console and look at school_mart.")


if __name__ == "__main__":
    main()
