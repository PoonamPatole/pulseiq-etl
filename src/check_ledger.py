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

TOLERANCE = 0.005


def check_ledger_balance():
    ledger = pd.read_excel(
        WORKBOOK,
        sheet_name="fact_ledger",
    )

    required_columns = {
    "entry_id",
    "debit",
    "credit",
    }
    missing = required_columns - set(ledger.columns)

    if missing:
        raise ValueError(
            f"Missing required ledger columns: {sorted(missing)}. "
            f"Available columns: {list(ledger.columns)}"
        )

    ledger["debit"] = pd.to_numeric(
        ledger["debit"], errors="coerce"
    )
    ledger["credit"] = pd.to_numeric(
        ledger["credit"], errors="coerce"
    )

    # Flag rows with missing amounts or journal-entry IDs.
    invalid_rows = (
    ledger["entry_id"].isna()
    | ledger["debit"].isna()
    | ledger["credit"].isna()
)

    # Compare total debits and credits for each journal entry.
    summary = ledger.groupby(
    "entry_id",
    dropna=False,
).agg(
    total_debit=("debit", "sum"),
    total_credit=("credit", "sum"),
    line_count=("entry_id", "size"),
).reset_index()

    summary["difference"] = (
        summary["total_debit"] - summary["total_credit"]
    ).round(2)

    unbalanced = summary[
        summary["difference"].abs() > TOLERANCE
    ].copy()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    unbalanced.to_csv(
        REPORT_DIR / "ledger_unbalanced_entries.csv",
        index=False,
    )

    invalid_rows.loc[invalid_rows].to_csv(
        REPORT_DIR / "ledger_invalid_rows.csv",
        index=False,
    )

    print(f"Ledger rows checked: {len(ledger)}")
    print(f"Journal entries checked: {len(summary)}")
    print(f"Unbalanced journal entries: {len(unbalanced)}")
    print(f"Rows with missing required values: {int(invalid_rows.sum())}")
    print("Reports saved in the logs folder.")


if __name__ == "__main__":
    check_ledger_balance()
