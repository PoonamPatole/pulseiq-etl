from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_DIR / "logs"


def test_invoice_arithmetic_has_no_issues():
    report_file = LOG_DIR / "invoice_arithmetic_issues.csv"
    assert report_file.exists(), "Run the invoice check first."

    report = pd.read_csv(report_file)
    assert len(report) == 0, "Unexpected invoice arithmetic issues found."


def test_known_overpayment_is_detected():
    report_file = LOG_DIR / "invoice_overpayment_issues.csv"
    assert report_file.exists(), "Run the invoice check first."

    report = pd.read_csv(report_file)
    assert "INV-00385" in set(report["invoice_id"])

    invoice = report.loc[report["invoice_id"] == "INV-00385"].iloc[0]
    assert abs(invoice["amount_paid"] - invoice["total_amount"] - 100) < 0.01
