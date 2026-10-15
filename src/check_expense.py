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


def check_expenses():
    expenses = pd.read_excel(
        WORKBOOK,
        sheet_name="fact_expense",
    )

    calculated_total = (
        expenses["amount_excl_gst"] + expenses["gst_amount"]
    )

    issue_mask = (
        calculated_total - expenses["total_amount"]
    ).abs() > 0.01

    issues = expenses.loc[issue_mask].copy()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    issues.to_csv(
        REPORT_DIR / "expense_total_issues.csv",
        index=False,
    )

    print(f"Expense rows checked: {len(expenses)}")
    print(f"Total mismatch issues found: {len(issues)}")
    print("Report saved in the logs folder.")


if __name__ == "__main__":
    check_expenses()
