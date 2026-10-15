
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
WORKBOOK = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "03_PulseIQ_Analytics_Star_Schema_Dataset.xlsx"
)

MONTHS_TO_REVIEW = [
    "2025-05",
    "2025-12",
    "2026-02",
    "2026-04",
    "2026-06",
]

SALARY_ACCOUNTS = ["5001", "5002", "5003", "5004", "5005"]


def inspect_differences():
    payroll = pd.read_excel(
        WORKBOOK,
        sheet_name="fact_payroll",
        usecols=["period_end_date", "employer_cost"],
    )

    payroll["period_end_date"] = pd.to_datetime(
        payroll["period_end_date"], errors="coerce"
    )
    payroll["month"] = payroll["period_end_date"].dt.strftime("%Y-%m")

    payroll_totals = payroll.groupby("month")["employer_cost"].sum()

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
    ].copy()

    ledger["month"] = ledger["posting_period"].astype(str)

    account_totals = (
        ledger.groupby(["month", "account_code"])["debit"]
        .sum()
        .unstack(fill_value=0)
        .reindex(columns=SALARY_ACCOUNTS, fill_value=0)
    )

    print("AGGREGATED DETAILS FOR MONTHS NEEDING REVIEW")
    print("-" * 65)

    for month in MONTHS_TO_REVIEW:
        print(f"\nMonth: {month}")
        print(f"Payroll employer cost: {payroll_totals.get(month, 0):,.2f}")

        if month in account_totals.index:
            print("Ledger debit totals by account:")
            print(account_totals.loc[month].round(2).to_string())
            ledger_total = account_totals.loc[month].sum()
        else:
            print("No matching ledger month found.")
            ledger_total = 0

        difference = payroll_totals.get(month, 0) - ledger_total
        print(f"Ledger salary-account total: {ledger_total:,.2f}")
        print(f"Difference (payroll - ledger): {difference:,.2f}")

    print("\nInspection complete. No individual records displayed.")


if __name__ == "__main__":
    inspect_differences()
