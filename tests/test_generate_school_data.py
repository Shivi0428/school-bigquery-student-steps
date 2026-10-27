"""Tests for the synthetic data generator. They run on any computer with no GCP account."""

import csv
from datetime import date
from pathlib import Path

import pytest

from scripts.generate_school_data import generate, school_days


@pytest.fixture(scope="module")
def out(tmp_path_factory) -> Path:
    folder = tmp_path_factory.mktemp("raw")
    generate(folder, students_count=20, start=date(2025, 4, 1), end=date(2025, 4, 30), seed=7)
    return folder


def read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def test_school_days_skip_weekends():
    days = school_days(date(2025, 4, 1), date(2025, 4, 13))  # two full weeks
    assert all(d.weekday() < 5 for d in days)
    assert len(days) == 9  # 1 Apr 2025 is a Tuesday, so 9 weekdays up to 13 Apr


def test_row_counts_match_the_plan(out):
    students = read(out / "students.csv")
    attendance = read(out / "attendance.csv")
    marks = read(out / "marks.csv")
    assert len(students) == 20
    assert len(attendance) == 20 * len(school_days(date(2025, 4, 1), date(2025, 4, 30)))
    assert len(marks) == 20 * 3 * 5  # 3 terms x 5 subjects


def test_student_ids_are_unique(out):
    ids = [int(r["student_id"]) for r in read(out / "students.csv")]
    assert len(ids) == len(set(ids))


def test_every_mark_points_to_a_student(out):
    ids = {int(r["student_id"]) for r in read(out / "students.csv")}
    assert all(int(r["student_id"]) in ids for r in read(out / "marks.csv"))


def test_scores_are_between_0_and_100(out):
    scores = [int(r["score"]) for r in read(out / "marks.csv")]
    assert min(scores) >= 0 and max(scores) <= 100


def test_attendance_is_only_0_or_1(out):
    assert {r["present"] for r in read(out / "attendance.csv")} <= {"0", "1"}


def test_same_seed_gives_same_data(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    generate(a, 5, date(2025, 4, 1), date(2025, 4, 5), seed=1)
    generate(b, 5, date(2025, 4, 1), date(2025, 4, 5), seed=1)
    assert (a / "marks.csv").read_text() == (b / "marks.csv").read_text()
