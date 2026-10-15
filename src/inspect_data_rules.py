
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
WORKBOOK = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "03_PulseIQ_Analytics_Star_Schema_Dataset.xlsx"
)


def inspect_data_rules():
    excel = pd.ExcelFile(WORKBOOK)

    print("DOCUMENTED DATA-QUALITY RULES")
    print("-" * 60)

    for sheet_name in [
        "dq_checks_catalog",
        "dq_known_issues",
        "data_contracts",
    ]:
        df = pd.read_excel(excel, sheet_name=sheet_name)

        print(f"\nSheet: {sheet_name}")
        print("Columns:", ", ".join(map(str, df.columns)))

        # Print only rows whose text mentions relevant payroll issues.
        text = df.fillna("").astype(str)
        row_text = text.agg(" ".join, axis=1)

        keywords = r"payroll|duplicate|employee.?key|orphan|reconcil"
        relevant = df[row_text.str.contains(keywords, case=False, regex=True)]

        if relevant.empty:
            print("No matching rule rows found.")
        else:
            print(relevant.to_string(index=False, max_colwidth=100))

    print("\nDocumentation inspection complete.")


def verify_planted_payroll_issues():
    payroll = pd.read_excel(
        WORKBOOK,
        sheet_name="fact_payroll",
        usecols=[
            "payroll_item_id",
            "employee_id",
            "employee_key",
            "run_id",
        ],
    )

    expected_ids = [
        "PI-X0001",
        "PI-X0002",
        "PI-X0003",
        "PI-X0004",
    ]

    found = payroll[payroll["payroll_item_id"].isin(expected_ids)].copy()

    print("PLANTED PAYROLL ISSUE VERIFICATION")
    print("-" * 50)
    print(f"Expected issue IDs: {len(expected_ids)}")
    print(f"IDs found: {len(found)}")
    print(f"Missing expected IDs: {len(set(expected_ids) - set(found['payroll_item_id']))}")

    duplicate_mask = payroll.duplicated(
        subset=["employee_id", "run_id"],
        keep=False,
    )
    duplicate_ids = set(payroll.loc[duplicate_mask, "payroll_item_id"])

    employee_dimension = pd.read_excel(
        WORKBOOK,
        sheet_name="dim_employee",
        usecols=["employee_id", "employee_key"],
    )

    known_employee_ids = set(employee_dimension["employee_id"].dropna())
    known_employee_keys = set(employee_dimension["employee_key"].dropna())

    found["duplicate_flag"] = found["payroll_item_id"].isin(duplicate_ids)
    found["employee_id_missing_from_dimension"] = (
        ~found["employee_id"].isin(known_employee_ids)
    )
    found["employee_key_missing_from_dimension"] = (
        found["employee_key"].isna()
        | ~found["employee_key"].isin(known_employee_keys)
    )

    print("\nIssue counts by documented ID group:")
    found["documented_group"] = found["payroll_item_id"].map(
        {
            "PI-X0001": "documented_duplicate",
            "PI-X0002": "documented_duplicate",
            "PI-X0003": "documented_orphan",
            "PI-X0004": "documented_orphan",
        }
    )

    summary = found.groupby("documented_group").agg(
        rows=("payroll_item_id", "size"),
        duplicate_flagged_rows=("duplicate_flag", "sum"),
        missing_employee_id_rows=("employee_id_missing_from_dimension", "sum"),
        missing_employee_key_rows=("employee_key_missing_from_dimension", "sum"),
    )

    print(summary.to_string())
    print("\nOnly aggregate counts displayed; no employee details shown.")


if __name__ == "__main__":
    verify_planted_payroll_issues()

if __name__ == "__main__":
    inspect_data_rules()
