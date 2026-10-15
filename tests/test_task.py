from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_DIR / "logs"


def test_known_task_date_issues_are_detected():
    report_file = LOG_DIR / "task_date_issues.csv"
    assert report_file.exists(), (
        "Task date report not found. Run the task check first."
    )

    report = pd.read_csv(report_file)
    assert len(report) == 12, (
        f"Expected 12 task date issues, found {len(report)}."
    )

    report["started_date"] = pd.to_datetime(
        report["started_date"], errors="coerce"
    )
    report["completed_date"] = pd.to_datetime(
        report["completed_date"], errors="coerce"
    )

    assert (
        report["completed_date"] < report["started_date"]
    ).all(), "Every reported task should finish before its start date."


def test_done_tasks_without_completion_dates_are_detected():
    report_file = LOG_DIR / "task_done_without_date_issues.csv"
    assert report_file.exists(), (
        "Task status report not found. Run the task check first."
    )

    report = pd.read_csv(report_file)
    assert len(report) == 8, (
        f"Expected 8 Done tasks without completion dates, found {len(report)}."
    )

    assert report["status"].astype("string").str.strip().str.casefold().eq("done").all()
    assert pd.to_datetime(
        report["completed_date"], errors="coerce"
    ).isna().all()
