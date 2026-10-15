
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
WORKBOOK = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "03_PulseIQ_Analytics_Star_Schema_Dataset.xlsx"
)
REPORT_DIR = PROJECT_DIR / "logs"


def check_invoices():
    invoices = pd.read_excel(
        WORKBOOK,
        sheet_name="fact_invoice",
    )

    # Check invoice arithmetic, allowing a tiny rounding tolerance.
    arithmetic_issue = (
        (invoices["subtotal"] + invoices["gst_amount"]
         - invoices["total_amount"]).abs() > 0.01
    )

    # Check for overpayments and negative balances.
    overpayment_issue = (
        (invoices["amount_paid"] > invoices["total_amount"] + 0.01)
        | (invoices["balance_due"] < -0.01)
    )

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    arithmetic_report = invoices.loc[arithmetic_issue].copy()
    overpayment_report = invoices.loc[overpayment_issue].copy()

    arithmetic_report.to_csv(
        REPORT_DIR / "invoice_arithmetic_issues.csv",
        index=False,
    )
    overpayment_report.to_csv(
        REPORT_DIR / "invoice_overpayment_issues.csv",
        index=False,
    )

    print(f"Invoice rows checked: {len(invoices)}")
    print(f"Arithmetic issues found: {len(arithmetic_report)}")
    print(f"Overpayment issues found: {len(overpayment_report)}")
    print("Reports saved in the logs folder.")


if __name__ == "__main__":
    check_invoices()
