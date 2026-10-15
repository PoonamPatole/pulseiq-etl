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


def check_task_quality():
    tasks = pd.read_excel(
        WORKBOOK,
        sheet_name="fact_task",
    )

    tasks["started_date"] = pd.to_datetime(
        tasks["started_date"], errors="coerce"
    )
    tasks["completed_date"] = pd.to_datetime(
        tasks["completed_date"], errors="coerce"
    )

    # A completion date must not be earlier than the start date.
    invalid_date_order = (
        tasks["started_date"].notna()
        & tasks["completed_date"].notna()
        & (tasks["completed_date"] < tasks["started_date"])
    )

    # A task marked Done must have a completion date.
    done_without_date = (
        tasks["status"].astype("string").str.strip().str.casefold().eq("done")
        & tasks["completed_date"].isna()
    )

    date_issues = tasks.loc[invalid_date_order].copy()
    status_issues = tasks.loc[done_without_date].copy()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    date_issues.to_csv(
        REPORT_DIR / "task_date_issues.csv",
        index=False,
    )
    status_issues.to_csv(
        REPORT_DIR / "task_done_without_date_issues.csv",
        index=False,
    )

    print(f"Task rows checked: {len(tasks)}")
    print(f"Completion-before-start issues: {len(date_issues)}")
    print(f"Done-without-completion-date issues: {len(status_issues)}")
    print("Reports saved in the logs folder.")


if __name__ == "__main__":
    check_task_quality()
