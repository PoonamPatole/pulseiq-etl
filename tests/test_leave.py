from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORT_FILE = PROJECT_DIR / "logs" / "leave_date_issues.csv"


def test_known_invalid_leave_dates_are_detected():
    assert REPORT_FILE.exists(), (
        "Leave-date report not found. Run the leave check first."
    )

    report = pd.read_csv(REPORT_FILE)

    assert len(report) == 2, (
        f"Expected 2 known leave-date issues, found {len(report)}."
    )

    report["start_date"] = pd.to_datetime(
        report["start_date"], errors="coerce"
    )
    report["end_date"] = pd.to_datetime(
        report["end_date"], errors="coerce"
    )

    invalid_order = report["end_date"] < report["start_date"]

    assert invalid_order.all(), (
        "Expected both reported records to have end dates before start dates."
    )
