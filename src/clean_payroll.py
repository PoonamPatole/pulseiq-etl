
from pathlib import Path
import pandas as pd
import os
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_DIR / ".env")

CLEAN_DIR = PROJECT_DIR / os.getenv("CLEAN_DATA_DIR", "data/clean")
REJECTED_DIR = PROJECT_DIR / os.getenv("REJECTED_DATA_DIR", "data/rejected")

WORKBOOK = PROJECT_DIR / os.getenv(
    "WORKBOOK_PATH",
    "data/raw/03_PulseIQ_Analytics_Star_Schema_Dataset.xlsx",
)

REJECTED_FILE = REJECTED_DIR / "fact_payroll_rejected.csv"
PENDING_FILE = CLEAN_DIR / "fact_payroll_pending_review.csv"
DUPLICATE_FILE = REJECTED_DIR / "fact_payroll_duplicates.csv"


def clean_payroll():
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    REJECTED_DIR.mkdir(parents=True, exist_ok=True)

    payroll = pd.read_excel(WORKBOOK, sheet_name="fact_payroll")

    employees = pd.read_excel(
        WORKBOOK,
        sheet_name="dim_employee",
        usecols=["employee_id", "employee_key"],
    )

    # Rule 1: identify employees with multiple rows per payroll run.
    duplicate_mask = payroll.duplicated(
        subset=["employee_id", "run_id"],
        keep=False,
    )

    # Rule 2: validate employee identifiers.
    known_employee_ids = set(employees["employee_id"].dropna())
    known_employee_keys = set(employees["employee_key"].dropna())

    invalid_employee_id = (
        payroll["employee_id"].isna()
        | ~payroll["employee_id"].isin(known_employee_ids)
    )

    invalid_employee_key = (
        payroll["employee_key"].isna()
        | ~payroll["employee_key"].isin(known_employee_keys)
    )

    orphan_mask = invalid_employee_id | invalid_employee_key

    # Record the reason each row was flagged.
    reasons = []

    for is_duplicate, is_orphan in zip(duplicate_mask, orphan_mask):
        row_reasons = []

        if is_duplicate:
            row_reasons.append("duplicate_employee_run")

        if is_orphan:
            row_reasons.append("unmatched_employee_reference")

        reasons.append("; ".join(row_reasons))

    # Quarantine only the documented extra duplicate rows.
    documented_duplicate_ids = {"PI-X0001", "PI-X0002"}

    planted_duplicate_mask = payroll["payroll_item_id"].isin(
        documented_duplicate_ids
    )

    # Also quarantine rows with unresolved employee references.
    rejected_mask = planted_duplicate_mask | orphan_mask

    rejected = payroll.loc[rejected_mask].copy()

    rejected["rejection_reason"] = [
        reasons[index]
        for index in payroll.index[rejected_mask]
    ]

    pending_review = payroll.loc[~rejected_mask].copy()


    rejected.to_csv(REJECTED_FILE, index=False)
    rejected.to_parquet(
        REJECTED_DIR / "fact_payroll_rejected.parquet",
        index=False,
    )

    pending_review.to_csv(PENDING_FILE, index=False)
    pending_review.to_parquet(
        CLEAN_DIR / "fact_payroll_pending_review.parquet",
        index=False,
    )

    # Refresh the report containing every row in a duplicate group.
    duplicate_report = payroll.loc[duplicate_mask].copy()
    duplicate_report["duplicate_reason"] = "duplicate_employee_run"
    duplicate_report.to_csv(DUPLICATE_FILE, index=False)

    print("PAYROLL CLEANING SUMMARY")
    print("-" * 45)
    print(f"Input rows: {len(payroll)}")
    print(f"Duplicate-flagged rows: {int(duplicate_mask.sum())}")
    print(f"Orphan-flagged rows: {int(orphan_mask.sum())}")
    print(f"Rejected unique rows: {len(rejected)}")
    print(f"Pending-review rows: {len(pending_review)}")

    print(f"Rejected file: {REJECTED_FILE}")
    print(f"Pending-review file: {PENDING_FILE}")
    print(f"Duplicate report: {DUPLICATE_FILE}")

    print("\nNo individual payroll records displayed.")


if __name__ == "__main__":
    clean_payroll()
