
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
WORKBOOK = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "03_PulseIQ_Analytics_Star_Schema_Dataset.xlsx"
)


def inspect_june_ledger():
    ledger = pd.read_excel(
        WORKBOOK,
        sheet_name="fact_ledger",
        usecols=["entry_id", "account_code", "debit", "credit"],
    )

    entry = ledger.loc[ledger["entry_id"] == "JE-002094"]

    if entry.empty:
        print("Documented journal entry was not found.")
        return

    # Show aggregated amounts by account, not individual ledger lines.
    summary = (
        entry.groupby("account_code", dropna=False)[["debit", "credit"]]
        .sum()
        .round(2)
    )

    print("JUNE 2026 JOURNAL ENTRY CHECK")
    print("-" * 45)
    print(summary.to_string())

    total_debit = entry["debit"].sum()
    total_credit = entry["credit"].sum()

    print("-" * 45)
    print(f"Total debits:  {total_debit:.2f}")
    print(f"Total credits: {total_credit:.2f}")
    print(f"Balance difference: {total_debit - total_credit:.2f}")


if __name__ == "__main__":
    inspect_june_ledger()
