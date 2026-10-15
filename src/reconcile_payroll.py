
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
WORKBOOK = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "03_PulseIQ_Analytics_Star_Schema_Dataset.xlsx"
)
REPORT = PROJECT_DIR / "logs" / "payroll_ledger_reconciliation_initial.csv"

TOLERANCE = 0.01
SALARY_ACCOUNTS = ["5001", "5002", "5003", "5004", "5005"]


def reconcile_payroll_to_ledger():
    # Read payroll totals by accounting month.
    payroll = pd.read_excel(
        WORKBOOK,
        sheet_name="fact_payroll",
        usecols=["period_end_date", "employer_cost"],
    )
    payroll["period_end_date"] = pd.to_datetime(
        payroll["period_end_date"], errors="coerce"
    )
    payroll["month"] = payroll["period_end_date"].dt.to_period("M")

    payroll_monthly = (
        payroll.groupby("month")["employer_cost"]
        .sum()
        .rename("payroll_employer_cost")
    )

    # Read only the ledger fields needed for reconciliation.
    ledger = pd.read_excel(
        WORKBOOK,
        sheet_name="fact_ledger",
        usecols=[
            "posting_period",
            "account_code",
            "debit",
        ],
    )

    ledger["account_code"] = (
        ledger["account_code"]
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
    )

    ledger = ledger[
        ledger["account_code"].isin(SALARY_ACCOUNTS)
    ].copy()

    ledger["month"] = pd.PeriodIndex(
        ledger["posting_period"].astype(str), freq="M"
    )

    ledger_monthly = (
        ledger.groupby("month")["debit"]
        .sum()
        .rename("ledger_salary_expense")
    )

    # Compare months present in either source.
    report = pd.concat(
        [payroll_monthly, ledger_monthly],
        axis=1,
    ).sort_index()

    report["payroll_employer_cost"] = (
        report["payroll_employer_cost"].fillna(0)
    )
    report["ledger_salary_expense"] = (
        report["ledger_salary_expense"].fillna(0)
    )

    report["difference"] = (
        report["payroll_employer_cost"]
        - report["ledger_salary_expense"]
    ).round(2)

    report["status"] = report["difference"].abs().le(
        TOLERANCE
    ).map({True: "PASS", False: "REVIEW"})

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(REPORT, index_label="month")

    print("INITIAL PAYROLL-TO-LEDGER RECONCILIATION")
    print("-" * 65)
    print(report.round(2).to_string())
    print("\nSummary")
    print(f"Months checked: {len(report)}")
    print(f"Passed: {(report['status'] == 'PASS').sum()}")
    print(f"Need review: {(report['status'] == 'REVIEW').sum()}")
    print(f"Report saved to: {REPORT}")
    print("\nThis is the initial source-data check; cleaning is not yet applied.")


if __name__ == "__main__":
    reconcile_payroll_to_ledger()
