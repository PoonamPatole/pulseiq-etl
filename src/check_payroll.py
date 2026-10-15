
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent

WORKBOOK = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "03_PulseIQ_Analytics_Star_Schema_Dataset.xlsx"
)

OUTPUT_FILE = PROJECT_DIR / "dq_payroll_audit.txt"


def audit_payroll():
    payroll = pd.read_excel(
        WORKBOOK,
        sheet_name="fact_payroll",
    )

    # Check whether each ledger journal entry balances.
    ledger = pd.read_excel(
        WORKBOOK,
        sheet_name="fact_ledger",
        usecols=["entry_id", "debit", "credit"],
    )

    entry_totals = ledger.groupby("entry_id").agg(
        total_debit=("debit", "sum"),
        total_credit=("credit", "sum"),
    )

    unbalanced_entries = (
        (entry_totals["total_debit"]
         - entry_totals["total_credit"]).abs()
        > 0.005
    )

    unbalanced_count = int(unbalanced_entries.sum())

    print("\nLedger balance validation:")
    print(f"Journal entries checked: {len(entry_totals)}")
    print(f"Unbalanced journal entries: {unbalanced_count}")

    # Check payroll employee keys against dim_employee.
    employees = pd.read_excel(
        WORKBOOK,
        sheet_name="dim_employee",
        usecols=["employee_key"],
    )

    known_keys = set(employees["employee_key"].dropna())

    missing_key_mask = (
        payroll["employee_key"].isna()
        | ~payroll["employee_key"].isin(known_keys)
    )

    missing_key_count = int(missing_key_mask.sum())

    # Check overlap between unmatched keys and duplicate combinations.
    duplicate_mask = payroll.duplicated(
        subset=["employee_id", "run_id"],
        keep=False,
    )

    overlap_count = int(
        (missing_key_mask & duplicate_mask).sum()
    )

    print(
        "Unmatched-key rows also flagged as duplicates: "
        f"{overlap_count}"
    )


    print("\nEmployee-key validation:")
    print(
        "Payroll rows with unmatched employee keys: "
        f"{missing_key_count}"
    )

    checks = []

    def record_check(name, issue_count, details):
        checks.append(
            {
                "Check": name,
                "Issue count": int(issue_count),
                "Details": details,
            }
        )

    # 1. Missing values in important fields
    required = [
        "payroll_item_id",
        "run_id",
        "employee_id",
        "employee_key",
        "period_end_date",
        "gross_pay",
        "net_pay",
    ]

    missing_count = int(
        payroll[required].isna().any(axis=1).sum()
    )

    record_check(
        "Missing required fields",
        missing_count,
        "Rows missing one or more required values",
    )

    # 2. Duplicate payroll item IDs
    duplicate_ids = int(
        payroll["payroll_item_id"].duplicated().sum()
    )

    record_check(
        "Duplicate payroll item IDs",
        duplicate_ids,
        "Repeated IDs after the first occurrence",
    )

    # 3. More than one row per employee per payroll run
    duplicate_employee_runs = int(
        payroll.duplicated(
            subset=["employee_id", "run_id"],
            keep=False,
        ).sum()
    )


    duplicate_rows = payroll[
        payroll.duplicated(
            subset=["employee_id", "run_id"],
            keep=False,
        )
    ]

    affected_runs = (
        duplicate_rows.groupby("run_id")
        .size()
        .reset_index(name="flagged_row_count")
    )

    print("\nDuplicate summary by payroll run:")
    print(f"Affected payroll runs: {len(affected_runs)}")
    print(
        "Rows involved in repeated combinations: "
        f"{len(duplicate_rows)}"
    )

    record_check(
        "Duplicate employee/run combinations",
        duplicate_employee_runs,
        "Rows belonging to repeated employee/run pairs",
    )

    # 4. Negative values in monetary fields
    money_columns = [
        "monthly_fixed_gross",
        "basic",
        "hra",
        "conveyance",
        "medical",
        "special_allowance",
        "earned_fixed_pay",
        "overtime_pay",
        "variable_pay",
        "gross_pay",
        "total_deductions",
        "net_pay",
        "employer_cost",
    ]

    negative_money = int(
        payroll[money_columns].lt(0).any(axis=1).sum()
    )

    record_check(
        "Negative monetary values",
        negative_money,
        "Rows with at least one negative amount",
    )

    # 5. Check payroll arithmetic
    expected_gross = (
        payroll["earned_fixed_pay"]
        + payroll["overtime_pay"]
        + payroll["variable_pay"]
    )

    gross_mismatch = int(
        (
            (payroll["gross_pay"] - expected_gross).abs()
            > 0.01
        ).sum()
    )

    record_check(
        "Gross pay arithmetic differences",
        gross_mismatch,
        "Rows where gross pay differs from its components",
    )

    expected_net = (
        payroll["gross_pay"] - payroll["total_deductions"]
    )

    net_mismatch = int(
        (
            (payroll["net_pay"] - expected_net).abs()
            > 0.01
        ).sum()
    )

    record_check(
        "Net pay arithmetic differences",
        net_mismatch,
        "Rows where net pay differs from gross pay minus deductions",
    )

    report = pd.DataFrame(checks)

    report.to_csv(
        OUTPUT_FILE,
        sep="\t",
        index=False,
    )

    print("Payroll audit completed.")
    print(f"Rows checked: {len(payroll)}")
    print(f"Audit report saved to: {OUTPUT_FILE}")
    print("\nIssue counts:")

    for item in checks:
        print(f"- {item['Check']}: {item['Issue count']}")

    print("\nNo individual payroll records were printed.")


if __name__ == "__main__":
    audit_payroll()
