
from pathlib import Path
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORT_FILE = PROJECT_DIR / "logs" / "payroll_reconciliation.csv"


def test_reconciliation_report_has_expected_months_and_statuses():
    """Check the report produced by the ETL pipeline."""
    assert REPORT_FILE.exists(), (
        "Reconciliation report not found. Run the ETL pipeline first."
    )

    report = pd.read_csv(REPORT_FILE)

    assert len(report) == 18
    assert set(report["status"]) == {"PASS", "REVIEW"}
    assert (report["status"] == "PASS").sum() == 17
    assert (report["status"] == "REVIEW").sum() == 1

    # Preserve the known June 2026 mismatch for investigation.
    june = report.loc[report["month"] == "2026-06"]
    assert len(june) == 1
    assert june.iloc[0]["status"] == "REVIEW"
    assert abs(june.iloc[0]["difference"] - (-18450.00)) < 0.01
