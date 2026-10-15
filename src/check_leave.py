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


def check_leave_dates():
    leave = pd.read_excel(
        WORKBOOK,
        sheet_name="fact_leave",
    )

    leave["start_date"] = pd.to_datetime(
        leave["start_date"], errors="coerce"
    )
    leave["end_date"] = pd.to_datetime(
        leave["end_date"], errors="coerce"
    )

    # Flag records with missing dates or an end date before the start.
    invalid_dates = (
        leave["start_date"].isna()
        | leave["end_date"].isna()
        | (leave["end_date"] < leave["start_date"])
    )

    issues = leave.loc[invalid_dates].copy()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    issues.to_csv(
        REPORT_DIR / "leave_date_issues.csv",
        index=False,
    )

    print(f"Leave rows checked: {len(leave)}")
    print(f"Invalid leave-date records found: {len(issues)}")
    print("Report saved in the logs folder.")


if __name__ == "__main__":
    check_leave_dates()
