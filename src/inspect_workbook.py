
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
WORKBOOK = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "03_PulseIQ_Analytics_Star_Schema_Dataset.xlsx"
)


def inspect_reconciliation_fields():
    print("PAYROLL MONTH SUMMARY")
    print("-" * 50)

    payroll = pd.read_excel(
        WORKBOOK,
        sheet_name="fact_payroll",
        usecols=["period_end_date", "employer_cost"],
    )

    payroll["period_end_date"] = pd.to_datetime(
        payroll["period_end_date"], errors="coerce"
    )

    payroll["month"] = payroll["period_end_date"].dt.to_period("M")

    payroll_monthly = payroll.groupby("month").agg(
        payroll_rows=("employer_cost", "size"),
        payroll_employer_cost=("employer_cost", "sum"),
    )

    print(payroll_monthly.to_string())

    print("\nLEDGER SALARY-ACCOUNT SUMMARY")
    print("-" * 50)

    ledger = pd.read_excel(
        WORKBOOK,
        sheet_name="fact_ledger",
        usecols=[
            "posting_period",
            "account_code",
            "debit",
            "credit",
            "signed_amount_debit_positive",
        ],
    )

    salary_accounts = ["5001", "5002", "5003", "5004", "5005"]

    ledger["account_code"] = (
        ledger["account_code"].astype(str).str.replace(r"\.0$", "", regex=True)
    )

    salary_ledger = ledger[
        ledger["account_code"].isin(salary_accounts)
    ].copy()

    print("Posting-period examples:")
    print(
        salary_ledger["posting_period"]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .sort_values()
        .head(12)
        .to_list()
    )

    print("\nMonthly totals by posting period:")
    monthly = salary_ledger.groupby("posting_period").agg(
        ledger_rows=("account_code", "size"),
        debit_total=("debit", "sum"),
        credit_total=("credit", "sum"),
        signed_total=("signed_amount_debit_positive", "sum"),
    )

    print(monthly.to_string())

    print("\nAccount-level sign summary:")
    account_summary = salary_ledger.groupby("account_code").agg(
        rows=("account_code", "size"),
        debit_total=("debit", "sum"),
        credit_total=("credit", "sum"),
        signed_total=("signed_amount_debit_positive", "sum"),
    )

    print(account_summary.to_string())
    print("\nInspection complete. No individual transactions displayed.")


if __name__ == "__main__":
    inspect_reconciliation_fields()
