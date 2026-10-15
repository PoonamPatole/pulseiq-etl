
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
WORKBOOK = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "03_PulseIQ_Analytics_Star_Schema_Dataset.xlsx"
)


def inspect_payroll_issues():
    payroll = pd.read_excel(
        WORKBOOK,
        sheet_name="fact_payroll",
        usecols=[
            "employee_id",
            "employee_key",
            "run_id",
            "period_end_date",
            "employer_cost",
        ],
    )

    employees = pd.read_excel(
        WORKBOOK,
        sheet_name="dim_employee",
        usecols=["employee_key"],
    )

    known_keys = set(employees["employee_key"].dropna())
    missing_key = (
        payroll["employee_key"].isna()
        | ~payroll["employee_key"].isin(known_keys)
    )

    duplicate = payroll.duplicated(
        subset=["employee_id", "run_id"],
        keep=False,
    )

    payroll["month"] = pd.to_datetime(
        payroll["period_end_date"], errors="coerce"
    ).dt.strftime("%Y-%m")

    payroll["duplicate_flag"] = duplicate
    payroll["unmatched_key_flag"] = missing_key

    print("MONTHLY IMPACT OF PAYROLL QUALITY ISSUES")
    print("-" * 60)

    summary = payroll.groupby("month").agg(
        total_rows=("employer_cost", "size"),
        duplicate_rows=("duplicate_flag", "sum"),
        duplicate_rows_employer_cost=(
            "employer_cost",
            lambda values: values[
                payroll.loc[values.index, "duplicate_flag"]
            ].sum(),
        ),
        unmatched_key_rows=("unmatched_key_flag", "sum"),
        unmatched_key_employer_cost=(
            "employer_cost",
            lambda values: values[
                payroll.loc[values.index, "unmatched_key_flag"]
            ].sum(),
        ),
    )

    months = ["2025-05", "2025-12", "2026-02", "2026-04", "2026-06"]
    print(summary.reindex(months).fillna(0).round(2).to_string())

    print("\nOverall counts")
    print(f"Rows checked: {len(payroll)}")
    print(f"Rows in duplicate combinations: {int(duplicate.sum())}")
    print(f"Rows with unmatched employee keys: {int(missing_key.sum())}")
    print(
        "Overlap between these two issue types:",
        int((duplicate & missing_key).sum()),
    )
    print("\nOnly monthly aggregates are shown; no individual rows displayed.")

def inspect_duplicate_patterns():
    payroll = pd.read_excel(
        WORKBOOK,
        sheet_name="fact_payroll",
        usecols=[
            "payroll_item_id",
            "employee_id",
            "employee_key",
            "run_id",
            "period_end_date",
            "employer_cost",
            "gross_pay",
            "net_pay",
        ],
    )

    duplicate_mask = payroll.duplicated(
        subset=["employee_id", "run_id"],
        keep=False,
    )
    duplicates = payroll.loc[duplicate_mask].copy()

    print("DUPLICATE PATTERN SUMMARY")
    print("-" * 50)

    print(f"Rows involved: {len(duplicates)}")
    print(
        "Distinct employee/run combinations:",
        duplicates[["employee_id", "run_id"]]
        .drop_duplicates()
        .shape[0],
    )

    # Show only grouped counts and totals, not individual records.
    summary = duplicates.groupby(
        ["period_end_date", "run_id"],
        dropna=False,
    ).agg(
        affected_rows=("payroll_item_id", "size"),
        distinct_payroll_item_ids=("payroll_item_id", "nunique"),
        distinct_employee_keys=("employee_key", "nunique"),
        distinct_employer_costs=("employer_cost", "nunique"),
        combined_employer_cost=("employer_cost", "sum"),
        distinct_gross_pay_values=("gross_pay", "nunique"),
        distinct_net_pay_values=("net_pay", "nunique"),
    )

    print(summary.to_string())
    print("\nNo individual payroll records displayed.")


if __name__ == "__main__":
    inspect_duplicate_patterns()


if __name__ == "__main__":
    inspect_payroll_issues()
