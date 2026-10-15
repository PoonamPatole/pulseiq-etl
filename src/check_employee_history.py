
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
REPORT_FILE = REPORT_DIR / "employee_history_issues.csv"


def check_employee_history():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    employees = pd.read_excel(
        WORKBOOK,
        sheet_name="dim_employee",
        usecols=["employee_id", "employee_key", "valid_from", "valid_to"],
    )

    employees["valid_from"] = pd.to_datetime(
        employees["valid_from"], errors="coerce"
    )
    employees["valid_to"] = pd.to_datetime(
        employees["valid_to"], errors="coerce"
    )

    issues = []

    for employee_id, group in employees.groupby("employee_id"):
        group = group.sort_values("valid_from")
        rows = list(
            group[
                ["employee_key", "valid_from", "valid_to"]
            ].itertuples(index=False, name=None)
        )

        for i in range(1, len(rows)):
            previous_key, previous_start, previous_end = rows[i - 1]
            current_key, current_start, current_end = rows[i]

            if pd.isna(previous_end) or previous_end >= current_start:
                issues.append({
                    "employee_id": employee_id,
                    "previous_employee_key": previous_key,
                    "previous_valid_from": previous_start,
                    "previous_valid_to": previous_end,
                    "current_employee_key": current_key,
                    "current_valid_from": current_start,
                    "current_valid_to": current_end,
                    "issue": "Overlapping employee history",
                })

    columns = [
        "employee_id",
        "previous_employee_key",
        "previous_valid_from",
        "previous_valid_to",
        "current_employee_key",
        "current_valid_from",
        "current_valid_to",
        "issue",
    ]

    report = pd.DataFrame(issues, columns=columns)
    report.to_csv(REPORT_FILE, index=False)

    print(f"Employee history issues found: {len(report)}")
    print(f"Report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    check_employee_history()
