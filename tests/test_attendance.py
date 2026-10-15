
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORT_FILE = PROJECT_DIR / "logs" / "attendance_after_exit_issues.csv"


def test_known_attendance_after_exit_records_are_detected():
    assert REPORT_FILE.exists(), (
        "Attendance report not found. Run the attendance check first."
    )

    report = pd.read_csv(REPORT_FILE)

    expected_ids = {
        "FA-X0001",
        "FA-X0002",
        "FA-X0003",
        "FA-X0004",
    }

    detected_ids = set(report["attendance_fact_id"])

    assert expected_ids.issubset(detected_ids), (
        f"Missing expected attendance issues: {expected_ids - detected_ids}"
    )
