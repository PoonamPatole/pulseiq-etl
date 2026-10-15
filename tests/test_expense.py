from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORT_FILE = PROJECT_DIR / "logs" / "expense_total_issues.csv"


def test_known_expense_total_mismatch_is_detected():
    assert REPORT_FILE.exists(), (
        "Expense report not found. Run the expense check first."
    )

    report = pd.read_csv(REPORT_FILE)

    assert len(report) == 1, (
        f"Expected 1 known expense issue, found {len(report)}."
    )

    expense = report.iloc[0]

    difference = (
        expense["total_amount"]
        - expense["amount_excl_gst"]
        - expense["gst_amount"]
    )

    assert abs(difference - 500) < 0.01, (
        f"Expected a ₹500 mismatch, found ₹{difference:.2f}."
    )
