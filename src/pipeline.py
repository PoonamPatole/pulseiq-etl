from pathlib import Path
import logging
import pandas as pd
from src.validation import (
    validate_employee_data,
    validate_employee_history,
)
from src.clean_payroll import clean_payroll
from src.reconcile_cleaned_payroll import reconcile_pending_payroll
from src.check_attendance import check_attendance_after_exit
from src.check_invoice import check_invoices
from src.check_expense import check_expenses
from src.check_leave import check_leave_dates
from src.check_task import check_task_quality
from src.check_ledger import check_ledger_balance
from src.clean_employee import clean_employee_data
from src.calculate_metrics import calculate_metrics
from dotenv import load_dotenv
import os

PROJECT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_DIR / ".env")

RAW_DIR = PROJECT_DIR / "data" / "raw"
LOG_DIR = PROJECT_DIR / os.getenv("LOG_DIR", "logs")

WORKBOOK = PROJECT_DIR / os.getenv(
    "WORKBOOK_PATH",
    "data/raw/03_PulseIQ_Analytics_Star_Schema_Dataset.xlsx",
)

LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "etl.log",
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def inspect_workbook():
    """Inspect the workbook and run the ETL steps."""

    if not WORKBOOK.exists():
        raise FileNotFoundError(f"Workbook not found: {WORKBOOK}")

    logging.info("Starting workbook inspection")
    excel_file = pd.ExcelFile(WORKBOOK)

    employee_df = pd.read_excel(
        excel_file,
        sheet_name="dim_employee",
    )

    validate_employee_data(employee_df)
    logging.info("Employee dimension validation passed.")
    print("Employee dimension validation: PASSED")

    try:
        validate_employee_history(employee_df)
        logging.info("Employee history validation passed.")
        print("Employee history validation: PASSED")
    except ValueError as exc:
        logging.warning("Employee history validation needs review: %s", exc)
        print(f"Employee history validation: REVIEW - {exc}")

        employee_id = str(exc).split("employee_id=")[-1]
        columns = ["employee_id", "employee_key", "valid_from", "valid_to"]

        history = employee_df.loc[
            employee_df["employee_id"].astype(str) == employee_id,
            columns,
        ].sort_values("valid_from")

        print("\nAffected employee history:")
        print(history.to_string(index=False))


    logging.info("Starting data quality checks")

    check_attendance_after_exit()
    check_invoices()
    check_expenses()
    check_leave_dates()
    check_task_quality()
    check_ledger_balance()

    logging.info("Data quality checks completed")
    print("Data quality checks completed. Review the logs folder for results.")


    logging.info("Starting employee cleaning")
    clean_employee_data()
    logging.info("Employee cleaning completed")

    logging.info("Starting payroll cleaning")
    clean_payroll()
    logging.info("Payroll cleaning completed")
    # logging.info("Starting payroll cleaning")
    # clean_payroll()
    # logging.info("Payroll cleaning completed")

    logging.info("Starting payroll reconciliation")
    reconcile_pending_payroll()
    logging.info("Payroll reconciliation completed")

    logging.info("Starting headcount and attrition metrics")
    calculate_metrics()
    logging.info("Headcount and attrition metrics completed")

    print("\nPulseIQ ETL pipeline")
    print(f"Workbook: {WORKBOOK.name}")
    print(f"Number of sheets: {len(excel_file.sheet_names)}")
    print("\nSheet inventory:")

    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(
            excel_file,
            sheet_name=sheet_name,
            nrows=0,
        )

        row_count = len(
            pd.read_excel(
                excel_file,
                sheet_name=sheet_name,
                usecols=[0],
            )
        )

        print(
            f"- {sheet_name}: "
            f"{row_count} rows, "
            f"{len(df.columns)} columns"
        )

    logging.info(
        "Workbook inspection completed: %s sheets",
        len(excel_file.sheet_names),
    )

    print("\nWorkbook inspection completed.")
    print(f"Log file: {LOG_DIR / 'etl.log'}")


if __name__ == "__main__":
    try:
        inspect_workbook()
    except Exception:
        logging.exception("Workbook inspection failed")
        raise
