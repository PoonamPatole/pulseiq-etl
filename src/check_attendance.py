
from pathlib import Path
import logging
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
LOG_DIR = PROJECT_DIR / "logs"

WORKBOOK = RAW_DIR / "03_PulseIQ_Analytics_Star_Schema_Dataset.xlsx"


def check_attendance_after_exit():
    """Identify attendance recorded after an employee's exit month."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    attendance = pd.read_excel(
        WORKBOOK,
        sheet_name="fact_attendance_monthly",
    )
    employees = pd.read_excel(
        WORKBOOK,
        sheet_name="dim_employee",
    )

    attendance["period_end_date"] = pd.to_datetime(
    attendance["period_end_date"], errors="coerce"
)
    employees["exit_date"] = pd.to_datetime(
        employees["exit_date"], errors="coerce"
    )

    employee_dates = employees[["employee_key", "exit_date"]].copy()
    employee_dates = employee_dates.dropna(subset=["employee_key"])
    employee_dates = employee_dates.drop_duplicates("employee_key")

    checked = attendance.merge(
        employee_dates,
        on="employee_key",
        how="left",
        validate="many_to_one",
        indicator=True,
    )

    unmatched = checked.loc[checked["_merge"] == "left_only"].copy()
    checked = checked.loc[checked["_merge"] == "both"].copy()

    after_exit = checked.loc[
        checked["exit_date"].notna()
        & checked["period_end_date"].notna()
        & (
            checked["period_end_date"].dt.to_period("M")
            > checked["exit_date"].dt.to_period("M")
        )
    ].copy()

    same_month = checked.loc[
        checked["exit_date"].notna()
        & checked["period_end_date"].notna()
        & (
            checked["period_end_date"].dt.to_period("M")
            == checked["exit_date"].dt.to_period("M")
        )
    ].copy()

    after_exit.to_csv(
        LOG_DIR / "attendance_after_exit_issues.csv", index=False
    )
    same_month.to_csv(
        LOG_DIR / "attendance_same_month_exit_review.csv", index=False
    )
    unmatched.to_csv(
        LOG_DIR / "attendance_unmatched_employee_keys.csv", index=False
    )

    print(f"Attendance rows checked: {len(attendance)}")
    print(f"Attendance after exit month: {len(after_exit)}")
    print(f"Same-month exit records for review: {len(same_month)}")
    print(f"Unmatched employee keys: {len(unmatched)}")
    print("Attendance reports saved in the logs folder.")

    return after_exit


if __name__ == "__main__":
    check_attendance_after_exit()
