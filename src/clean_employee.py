from pathlib import Path
import logging
import pandas as pd
import os
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_DIR / ".env")

RAW_DIR = PROJECT_DIR / "data" / "raw"
CLEAN_DIR = PROJECT_DIR / os.getenv("CLEAN_DATA_DIR", "data/clean")
REJECTED_DIR = PROJECT_DIR / os.getenv("REJECTED_DATA_DIR", "data/rejected")
LOG_DIR = PROJECT_DIR / os.getenv("LOG_DIR", "logs")

WORKBOOK = PROJECT_DIR / os.getenv(
    "WORKBOOK_PATH",
    "data/raw/03_PulseIQ_Analytics_Star_Schema_Dataset.xlsx",
)


def clean_employee_data():
    """Clean the employee dimension while preserving historical versions."""
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    REJECTED_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logging.info("Starting employee dimension cleaning")

    df = pd.read_excel(WORKBOOK, sheet_name="dim_employee")
    input_rows = len(df)

    # Trim whitespace in text columns.
    text_columns = df.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in text_columns:
        df[column] = df[column].str.strip()
        df[column] = df[column].replace("", pd.NA)

    # Convert date columns. Null exit_date and valid_to values are allowed.
    date_columns = [
        "date_of_birth",
        "hire_date",
        "exit_date",
        "valid_from",
        "valid_to",
    ]

    for column in date_columns:
        df[column] = pd.to_datetime(df[column], errors="coerce")

    # Employee key must be a valid integer.
    original_key = df["employee_key"].copy()
    df["employee_key"] = pd.to_numeric(
        df["employee_key"], errors="coerce"
    )

    invalid_key_format = (
        df["employee_key"].notna()
        & (df["employee_key"] % 1 != 0)
    )
    df.loc[invalid_key_format, "employee_key"] = pd.NA

    df["employee_key"] = df["employee_key"].astype("Int64")

    # Required fields for identifying and dating an employee version.
    required_columns = [
        "employee_key",
        "employee_id",
        "full_name",
        "hire_date",
        "valid_from",
    ]

    invalid_mask = df[required_columns].isna().any(axis=1)
    invalid_mask |= invalid_key_format

    # Reject duplicate employee version keys, keeping the first occurrence.
    duplicate_mask = (
        df["employee_key"].notna()
        & df["employee_key"].duplicated(keep="first")
    )

    rejected_mask = invalid_mask | duplicate_mask

    rejected = df.loc[rejected_mask].copy()
    valid = df.loc[~rejected_mask].copy()

    # Record why each rejected row was excluded.
    reasons = []
    for index in rejected.index:
        row_reasons = []

        if invalid_mask.loc[index]:
            row_reasons.append("Missing or invalid required field")

        if duplicate_mask.loc[index]:
            row_reasons.append("Duplicate employee_key")

        reasons.append("; ".join(row_reasons))

    rejected["rejection_reason"] = reasons

    # Add useful hiring and tenure helper columns.
    valid["hire_month"] = valid["hire_date"].dt.month
    valid["hire_year"] = valid["hire_date"].dt.year

    today = pd.Timestamp.today().normalize()
    effective_end = valid["exit_date"].fillna(today)

    valid["tenure_days"] = (
        effective_end - valid["hire_date"]
    ).dt.days

    # Flag impossible negative tenure rather than silently retaining it.
    negative_tenure = valid["tenure_days"] < 0

    if negative_tenure.any():
        additional_rejected = valid.loc[negative_tenure].copy()
        additional_rejected["rejection_reason"] = (
            "Exit date or current date is before hire date"
        )

        rejected = pd.concat(
            [rejected, additional_rejected],
            ignore_index=True,
        )
        valid = valid.loc[~negative_tenure].copy()


    valid.to_csv(
        CLEAN_DIR / "dim_employee_clean.csv", index=False
    )
    valid.to_parquet(
        CLEAN_DIR / "dim_employee_clean.parquet", index=False
    )

    rejected.to_csv(
        REJECTED_DIR / "dim_employee_rejected.csv", index=False
    )
    rejected.to_parquet(
        REJECTED_DIR / "dim_employee_rejected.parquet", index=False
    )


    summary = (
        f"Input rows: {input_rows}\n"
        f"Clean rows: {len(valid)}\n"
        f"Rejected rows: {len(rejected)}\n"
    )

    (LOG_DIR / "employee_cleaning_summary.txt").write_text(
        summary, encoding="utf-8"
    )

    logging.info(
        "Employee cleaning finished: input=%s clean=%s rejected=%s",
        input_rows,
        len(valid),
        len(rejected),
    )

    print("EMPLOYEE CLEANING SUMMARY")
    print("-" * 35)
    print(summary)
    print("Clean file: data/clean/dim_employee_clean.csv")
    print("Rejected file: data/rejected/dim_employee_rejected.csv")
    print("Employee history overlaps are checked separately.")


if __name__ == "__main__":
    clean_employee_data()
