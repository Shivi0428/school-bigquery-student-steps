"""Generate synthetic school data as CSV files for the BigQuery student project.

Three tables are created:
  students.csv    one row per student
  attendance.csv  one row per student per school day (1 = present, 0 = absent)
  marks.csv       one row per student per subject per term

Everything is random but seeded, so the same command always gives the same files.
No real student data is used.
"""

from __future__ import annotations

import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

SUBJECTS = ["Maths", "English", "Science", "Computing", "History"]
CLASSES = ["Class 7", "Class 8", "Class 9", "Class 10"]
SECTIONS = ["A", "B"]
FIRST_NAMES = ["Aarav", "Diya", "Kabir", "Meera", "Rohan", "Ananya", "Vihaan", "Ishita",
               "Arjun", "Sara", "Dev", "Nisha", "Aditya", "Kavya", "Yash", "Riya"]
LAST_NAMES = ["Sharma", "Verma", "Gupta", "Singh", "Patel", "Khan", "Mehta", "Iyer"]


def school_days(start: date, end: date) -> list[date]:
    """Monday to Friday between start and end, both included."""
    days = []
    current = start
    while current <= end:
        if current.weekday() < 5:
            days.append(current)
        current += timedelta(days=1)
    return days


def generate(out_dir: Path, students_count: int, start: date, end: date, seed: int) -> dict[str, int]:
    rng = random.Random(seed)
    out_dir.mkdir(parents=True, exist_ok=True)

    students = []
    for i in range(1, students_count + 1):
        students.append({
            "student_id": i,
            "full_name": f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
            "class_name": rng.choice(CLASSES),
            "section": rng.choice(SECTIONS),
            # Each student has a personal "attendance habit" between 65% and 99%.
            "attendance_habit": round(rng.uniform(0.65, 0.99), 2),
            "ability": round(rng.uniform(35, 90), 1),
        })

    days = school_days(start, end)
    attendance_rows = []
    for s in students:
        for d in days:
            present = 1 if rng.random() < s["attendance_habit"] else 0
            attendance_rows.append({"student_id": s["student_id"], "school_date": d.isoformat(), "present": present})

    mark_rows = []
    for s in students:
        for term in (1, 2, 3):
            for subject in SUBJECTS:
                # Score is around the student's ability, with some random spread, kept between 0 and 100.
                score = max(0, min(100, round(rng.gauss(s["ability"], 8))))
                mark_rows.append({"student_id": s["student_id"], "subject": subject, "term": term, "score": score})

    _write(out_dir / "students.csv", ["student_id", "full_name", "class_name", "section", "attendance_habit", "ability"],
           [{k: s[k] for k in ("student_id", "full_name", "class_name", "section", "attendance_habit", "ability")} for s in students])
    _write(out_dir / "attendance.csv", ["student_id", "school_date", "present"], attendance_rows)
    _write(out_dir / "marks.csv", ["student_id", "subject", "term", "score"], mark_rows)

    return {"students": len(students), "attendance": len(attendance_rows), "marks": len(mark_rows)}


def _write(path: Path, header: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=Path("data/raw"), help="output folder")
    parser.add_argument("--students", type=int, default=120, help="how many students")
    parser.add_argument("--start", type=date.fromisoformat, default=date(2025, 4, 1))
    parser.add_argument("--end", type=date.fromisoformat, default=date(2025, 7, 31))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    counts = generate(args.out, args.students, args.start, args.end, args.seed)
    for name, n in counts.items():
        print(f"{name:<12} {n:>8,} rows")


if __name__ == "__main__":
    main()
