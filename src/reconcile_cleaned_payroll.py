
from pathlib import Path
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_DIR / "logs"
REPORT_FILE = REPORT_DIR / "payroll_reconciliation.csv"

PAYROLL_FILE = (
    PROJECT_DIR
    / "data"
    / "clean"
    / "fact_payroll_pending_review.csv"
)

WORKBOOK = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "03_PulseIQ_Analytics_Star_Schema_Dataset.xlsx"
)

SALARY_ACCOUNTS = ["5001", "5002", "5003", "5004", "5005"]
TOLERANCE = 0.01


def reconcile_pending_payroll():
    payroll = pd.read_csv(PAYROLL_FILE)
    payroll["period_end_date"] = pd.to_datetime(
        payroll["period_end_date"], errors="coerce"
    )
    payroll["month"] = payroll["period_end_date"].dt.strftime("%Y-%m")

    payroll_monthly = (
        payroll.groupby("month")["employer_cost"]
        .sum()
        .rename("payroll_employer_cost")
    )


    ledger = pd.read_excel(
        WORKBOOK,
        sheet_name="fact_ledger",
        usecols=["posting_period", "account_code", "debit"],
    )

    ledger["account_code"] = (
        ledger["account_code"]
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
    )
    ledger = ledger[
        ledger["account_code"].isin(SALARY_ACCOUNTS)
    ]

    ledger_monthly = (
        ledger.groupby("posting_period")["debit"]
        .sum()
        .rename("ledger_salary_expense")
    )

    report = pd.concat(
        [payroll_monthly, ledger_monthly],
        axis=1,
    ).fillna(0).sort_index()

    report["difference"] = (
        report["payroll_employer_cost"]
        - report["ledger_salary_expense"]
    ).round(2)

    report["status"] = report["difference"].abs().le(
        TOLERANCE
    ).map({True: "PASS", False: "REVIEW"})

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report.to_csv(REPORT_FILE, index=True, index_label="month")
    print(f"\nReport saved to: {REPORT_FILE}")

    print("PENDING-REVIEW PAYROLL RECONCILIATION")
    print("-" * 60)
    print(report.round(2).to_string())
    print("\nSummary")
    print(f"Months checked: {len(report)}")
    print(f"Passed: {(report['status'] == 'PASS').sum()}")
    print(f"Need review: {(report['status'] == 'REVIEW').sum()}")
    print("\nThese rows still require all remaining data-quality checks.")


if __name__ == "__main__":
    reconcile_pending_payroll()
