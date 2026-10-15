
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
CLEAN_DIR = PROJECT_DIR / "data" / "clean"

WORKBOOK = RAW_DIR / "03_PulseIQ_Analytics_Star_Schema_Dataset.xlsx"
OUTPUT_FILE = CLEAN_DIR / "headcount_metrics.csv"


def calculate_metrics():
    """Verify and calculate the five official headcount and attrition metrics."""
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_excel(
        WORKBOOK,
        sheet_name="fact_headcount_monthly",
    )

    df["month_start_date"] = pd.to_datetime(
        df["month_start_date"], errors="coerce"
    )

    required = [
        "month_start_date",
        "department_id",
        "headcount_start",
        "hires",
        "exits",
        "headcount_end",
        "attrition_rate_monthly_pct",
    ]

    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if df[required].isna().any().any():
        raise ValueError("Required metric columns contain missing values.")

    if df.duplicated(["department_id", "month_start_date"]).any():
        raise ValueError("Duplicate department-month rows detected.")

    df = df.sort_values(
        ["department_id", "month_start_date"]
    ).copy()

    # M01: Headcount at month-end
    df["M01_headcount"] = df["headcount_end"]

    # M02: Hires during the month
    df["M02_hires"] = df["hires"]

    # M03: Exits during the month
    df["M03_exits"] = df["exits"]

    # M04: Monthly attrition; verify against the official formula.
    df["M04_monthly_attrition_pct"] = (
        df["exits"].div(df["headcount_start"].where(df["headcount_start"] != 0))
        * 100
    )

    df["M04_source_difference_pct_points"] = (
        df["M04_monthly_attrition_pct"]
        - df["attrition_rate_monthly_pct"]
    )

    # M05: Rolling 12-month attrition within each department.
    grouped = df.groupby("department_id", sort=False)

    df["M05_exits_12m"] = grouped["exits"].transform(
        lambda values: values.rolling(12, min_periods=12).sum()
    )

    df["M05_average_headcount_12m"] = grouped["headcount_end"].transform(
        lambda values: values.rolling(12, min_periods=12).mean()
    )

    df["M05_rolling_attrition_pct"] = (
        df["M05_exits_12m"]
        .div(df["M05_average_headcount_12m"].where(
            df["M05_average_headcount_12m"] != 0
        ))
        * 100
    )

    # Reporting suppression: hide small-group results.
    # Attrition metrics require at least 10 people.
    df.loc[
        df["headcount_start"] < 10,
        ["M04_monthly_attrition_pct"],
    ] = pd.NA

    df.loc[
        df["M05_average_headcount_12m"] < 10,
        ["M05_rolling_attrition_pct"],
    ] = pd.NA

    # Headcount, hires and exits require a minimum group size of 5.
    small_groups = df["headcount_end"] < 5
    df.loc[small_groups, ["M01_headcount", "M02_hires", "M03_exits"]] = pd.NA

    df.to_csv(OUTPUT_FILE, index=False)

    print("HEADCOUNT METRICS SUMMARY")
    print("-------------------------")
    print(f"Source rows: {len(df)}")
    print(f"Departments: {df['department_id'].nunique()}")
    print(f"Months: {df['month_start_date'].nunique()}")
    print(
        "Monthly attrition source mismatches:",
        int(
            (
                df["M04_source_difference_pct_points"].abs() > 0.01
            ).sum()
        ),
    )
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    calculate_metrics()
