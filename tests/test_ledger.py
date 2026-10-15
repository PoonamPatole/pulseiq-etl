from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_DIR / "logs"


def test_ledger_has_no_unbalanced_entries():
    report_file = LOG_DIR / "ledger_unbalanced_entries.csv"
    assert report_file.exists(), (
        "Ledger report not found. Run the ledger check first."
    )

    report = pd.read_csv(report_file)
    assert len(report) == 0, (
        f"Expected no unbalanced entries, found {len(report)}."
    )


def test_ledger_has_no_rows_with_missing_required_values():
    report_file = LOG_DIR / "ledger_invalid_rows.csv"
    assert report_file.exists(), (
        "Ledger invalid-row report not found. Run the ledger check first."
    )

    report = pd.read_csv(report_file)
    assert len(report) == 0, (
        f"Expected no invalid ledger rows, found {len(report)}."
    )
