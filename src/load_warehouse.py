import os
import pandas as pd
import psycopg
from psycopg import sql

DATABASE_URL = "postgresql://wos:wos@localhost:5432/pulseiq_wh"

employee_file = "data/clean/dim_employee_clean.csv"
payroll_file = "data/clean/fact_payroll_pending_review.csv"

employees = pd.read_csv(employee_file)
payroll = pd.read_csv(payroll_file)

def clean_value(value):
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        employee_columns = [
            "employee_key", "employee_id", "full_name", "gender",
            "date_of_birth", "hire_date", "exit_date", "employment_status",
            "employment_type", "department_id", "role_id", "role_title",
            "job_level", "manager_id", "work_location", "work_mode",
            "highest_education", "valid_from", "valid_to", "is_current",
            "change_reason"
        ]

        employee_sql = """
            INSERT INTO dw.dim_employee (
                employee_key, employee_id, full_name, gender, date_of_birth,
                hire_date, exit_date, employment_status, employment_type,
                department_id, role_id, role_title, job_level, manager_id,
                work_location, work_mode, highest_education, valid_from,
                valid_to, is_current, change_reason
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (employee_id, valid_from) DO UPDATE SET
                employee_key = EXCLUDED.employee_key,
                full_name = EXCLUDED.full_name,
                department_id = EXCLUDED.department_id,
                role_id = EXCLUDED.role_id,
                valid_to = EXCLUDED.valid_to,
                is_current = EXCLUDED.is_current,
                change_reason = EXCLUDED.change_reason
        """

        for row in employees[employee_columns].itertuples(index=False, name=None):
            cur.execute(employee_sql, tuple(clean_value(v) for v in row))

        payroll_columns = [
            "payroll_item_id", "run_id", "employee_id", "date_key",
            "employee_key", "period_end_date", "department_id", "role_id",
            "payable_days", "lop_days", "overtime_hours_paid",
            "variable_pay_type", "monthly_fixed_gross", "basic", "hra",
            "conveyance", "medical", "special_allowance", "earned_fixed_pay",
            "overtime_pay", "variable_pay", "gross_pay", "pf_employee",
            "esi_employee", "professional_tax", "tds", "other_deductions",
            "total_deductions", "net_pay", "pf_employer", "esi_employer",
            "employer_cost", "headcount_flag"
        ]

        payroll_sql = """
            INSERT INTO dw.fact_payroll (
                payroll_item_id, run_id, employee_id, date_key, employee_key,
                period_end_date, department_id, role_id, payable_days, lop_days,
                overtime_hours_paid, variable_pay_type, monthly_fixed_gross,
                basic, hra, conveyance, medical, special_allowance,
                earned_fixed_pay, overtime_pay, variable_pay, gross_pay,
                pf_employee, esi_employee, professional_tax, tds,
                other_deductions, total_deductions, net_pay, pf_employer,
                esi_employer, employer_cost, headcount_flag
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (payroll_item_id) DO UPDATE SET
                run_id = EXCLUDED.run_id,
                employee_key = EXCLUDED.employee_key,
                period_end_date = EXCLUDED.period_end_date,
                department_id = EXCLUDED.department_id,
                role_id = EXCLUDED.role_id,
                gross_pay = EXCLUDED.gross_pay,
                net_pay = EXCLUDED.net_pay,
                employer_cost = EXCLUDED.employer_cost
        """

        for row in payroll[payroll_columns].itertuples(index=False, name=None):
            cur.execute(payroll_sql, tuple(clean_value(v) for v in row))

print(f"Loaded {len(employees)} employee rows and {len(payroll)} payroll rows.")


# Load department, role, and leave type dimensions from the source workbook.
import pandas as pd
import psycopg

DATABASE_URL = "postgresql://wos:wos@localhost:5432/pulseiq_wh"
SOURCE_FILE = "data/raw/01_LedgerForge_Python_Master_Dataset.xlsx"

def load_dimension(sheet_name, table_name, columns, key_column):
    data = pd.read_excel(SOURCE_FILE, sheet_name=sheet_name)
    data = data[columns]

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            column_names = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(columns))
            update_columns = [
                column for column in columns if column != key_column
            ]
            updates = ", ".join(
                f"{column} = EXCLUDED.{column}"
                for column in update_columns
            )

            query = f"""
                INSERT INTO dw.{table_name} ({column_names})
                VALUES ({placeholders})
                ON CONFLICT ({key_column}) DO UPDATE SET {updates}
            """

            for row in data.itertuples(index=False, name=None):
                values = tuple(
                    None if pd.isna(value) else value
                    for value in row
                )
                cur.execute(query, values)

    print(f"Loaded {len(data)} rows into dw.{table_name}")


load_dimension(
    "departments",
    "dim_department",
    ["department_id", "department_name", "cost_center", "description"],
    "department_id",
)

load_dimension(
    "roles",
    "dim_role",
    [
        "role_id", "department_id", "role_title", "level", "grade",
        "band_min_annual", "band_mid_annual", "band_max_annual",
        "overtime_eligible", "band_year",
    ],
    "role_id",
)

load_dimension(
    "leave_types",
    "dim_leave_type",
    [
        "leave_type_code", "leave_type_name", "pay_type",
        "annual_quota_days", "prorated_for_joiners",
        "carry_forward_allowed", "max_carry_forward_days", "policy_note",
    ],
    "leave_type_code",
)


# Load date dimension and monthly attendance fact.
attendance = pd.read_excel(SOURCE_FILE, sheet_name="attendance")
attendance["attendance_date"] = pd.to_datetime(attendance["attendance_date"])
attendance["month"] = attendance["attendance_date"].dt.to_period("M").dt.to_timestamp()
attendance["period_end_date"] = attendance["month"] + pd.offsets.MonthEnd(0)

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        # Create the date dimension for all attendance dates.
        dates = pd.date_range(
            attendance["attendance_date"].min(),
            attendance["attendance_date"].max(),
            freq="D",
        )

        for date in dates:
            date_value = date.date()
            date_key = int(date.strftime("%Y%m%d"))
            cur.execute(
                """
                INSERT INTO dw.dim_date (date_key, full_date, year, month, day)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (date_key) DO NOTHING
                """,
                (date_key, date_value, date.year, date.month, date.day),
            )

        # Aggregate attendance to one row per employee per month.
        attendance["present_flag"] = attendance["status"].eq("PRESENT").astype(int)
        attendance["wfh_flag"] = attendance["status"].eq("WFH").astype(int)
        attendance["half_day_flag"] = attendance["status"].eq("HALF_DAY_UNPAID").astype(int)
        attendance["paid_leave_flag"] = attendance["status"].eq("PAID_LEAVE").astype(int)
        attendance["unpaid_absence_flag"] = attendance["status"].isin(
            ["ABSENT_LOP", "UNPAID_LEAVE"]
        ).astype(int)
        attendance["late_flag"] = pd.to_numeric(
            attendance["late_flag"], errors="coerce"
        ).fillna(0)

        monthly = attendance.groupby(
            ["employee_id", "month"], dropna=False
        ).agg(
            department_id=("department_id", "last"),
            scheduled_days=("attendance_id", "count"),
            present_days=("present_flag", "sum"),
            wfh_days=("wfh_flag", "sum"),
            half_days_unpaid=("half_day_flag", "sum"),
            paid_leave_days=("paid_leave_flag", "sum"),
            unpaid_absence_days=("unpaid_absence_flag", "sum"),
            late_arrivals=("late_flag", "sum"),
            avg_hours_worked=("hours_worked", "mean"),
            overtime_hours=("overtime_hours", "sum"),
        ).reset_index()

        monthly["attendance_rate"] = (
            (monthly["present_days"] + monthly["wfh_days"])
            / monthly["scheduled_days"]
        )

        for row in monthly.itertuples(index=False):
            employee_id = row.employee_id
            month_start = row.month.date()
            period_end = (row.month + pd.offsets.MonthEnd(0)).date()
            date_key = int(row.month.strftime("%Y%m%d"))

            cur.execute(
                """
                SELECT employee_key
                FROM dw.dim_employee
                WHERE employee_id = %s
                  AND valid_from <= %s
                  AND valid_to >= %s
                ORDER BY valid_from DESC
                LIMIT 1
                """,
                (employee_id, period_end, period_end),
            )
            result = cur.fetchone()
            employee_key = result[0] if result else None

            cur.execute(
                """
                INSERT INTO dw.fact_attendance_monthly (
                    employee_id, employee_key, date_key, department_id,
                    scheduled_days, present_days, wfh_days, half_days_unpaid,
                    paid_leave_days, unpaid_absence_days, late_arrivals,
                    avg_hours_worked, overtime_hours, attendance_rate,
                    period_end_date
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (employee_id, period_end_date) DO UPDATE SET
                    employee_key = EXCLUDED.employee_key,
                    date_key = EXCLUDED.date_key,
                    department_id = EXCLUDED.department_id,
                    scheduled_days = EXCLUDED.scheduled_days,
                    present_days = EXCLUDED.present_days,
                    wfh_days = EXCLUDED.wfh_days,
                    half_days_unpaid = EXCLUDED.half_days_unpaid,
                    paid_leave_days = EXCLUDED.paid_leave_days,
                    unpaid_absence_days = EXCLUDED.unpaid_absence_days,
                    late_arrivals = EXCLUDED.late_arrivals,
                    avg_hours_worked = EXCLUDED.avg_hours_worked,
                    overtime_hours = EXCLUDED.overtime_hours,
                    attendance_rate = EXCLUDED.attendance_rate
                """,
                (
                    employee_id, employee_key, date_key, row.department_id,
                    row.scheduled_days, row.present_days, row.wfh_days,
                    row.half_days_unpaid, row.paid_leave_days,
                    row.unpaid_absence_days, int(row.late_arrivals),
                    None if pd.isna(row.avg_hours_worked) else row.avg_hours_worked,
                    None if pd.isna(row.overtime_hours) else row.overtime_hours,
                    row.attendance_rate, period_end,
                ),
            )

print(f"Loaded {len(monthly)} monthly attendance rows.")


# Load leave requests.
leave_data = pd.read_excel(SOURCE_FILE, sheet_name="leave_requests")

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        for row in leave_data.itertuples(index=False):
            start_date = pd.to_datetime(row.start_date).date()
            end_date = pd.to_datetime(row.end_date).date()
            start_date_key = int(start_date.strftime("%Y%m%d"))
            end_date_key = int(end_date.strftime("%Y%m%d"))

            cur.execute(
                """
                INSERT INTO dw.dim_date (date_key, full_date, year, month, day)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (date_key) DO NOTHING
                """,
                (
                    start_date_key, start_date,
                    start_date.year, start_date.month, start_date.day,
                ),
            )
            cur.execute(
                """
                INSERT INTO dw.dim_date (date_key, full_date, year, month, day)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (date_key) DO NOTHING
                """,
                (
                    end_date_key, end_date,
                    end_date.year, end_date.month, end_date.day,
                ),
            )

            cur.execute(
                """
                SELECT employee_key
                FROM dw.dim_employee
                WHERE employee_id = %s
                  AND valid_from <= %s
                  AND valid_to >= %s
                ORDER BY valid_from DESC
                LIMIT 1
                """,
                (row.employee_id, start_date, start_date),
            )
            result = cur.fetchone()
            employee_key = result[0] if result else None

            cur.execute(
                """
                INSERT INTO dw.fact_leave (
                    leave_request_id, employee_id, employee_key,
                    leave_type_code, start_date_key, end_date_key,
                    start_date, end_date, days, status, applied_on,
                    decided_on, approver_id, reason
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (leave_request_id) DO UPDATE SET
                    employee_key = EXCLUDED.employee_key,
                    leave_type_code = EXCLUDED.leave_type_code,
                    start_date_key = EXCLUDED.start_date_key,
                    end_date_key = EXCLUDED.end_date_key,
                    start_date = EXCLUDED.start_date,
                    end_date = EXCLUDED.end_date,
                    days = EXCLUDED.days,
                    status = EXCLUDED.status,
                    applied_on = EXCLUDED.applied_on,
                    decided_on = EXCLUDED.decided_on,
                    approver_id = EXCLUDED.approver_id,
                    reason = EXCLUDED.reason
                """,
                (
                    str(row.leave_request_id),
                    row.employee_id,
                    employee_key,
                    row.leave_type_code,
                    start_date_key,
                    end_date_key,
                    start_date,
                    end_date,
                    None if pd.isna(row.days) else row.days,
                    row.status,
                    None if pd.isna(row.applied_on) else pd.to_datetime(row.applied_on).date(),
                    None if pd.isna(row.decided_on) else pd.to_datetime(row.decided_on).date(),
                    None if pd.isna(row.approver_id) else row.approver_id,
                    None if pd.isna(row.reason) else row.reason,
                ),
            )

print(f"Loaded {len(leave_data)} leave request rows.")


# Load daily attendance records.
daily_attendance = pd.read_excel(SOURCE_FILE, sheet_name="attendance")

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        for row in daily_attendance.itertuples(index=False):
            attendance_date = pd.to_datetime(row.attendance_date).date()
            date_key = int(attendance_date.strftime("%Y%m%d"))

            cur.execute(
                """
                SELECT employee_key
                FROM dw.dim_employee
                WHERE employee_id = %s
                  AND valid_from <= %s
                  AND valid_to >= %s
                ORDER BY valid_from DESC
                LIMIT 1
                """,
                (row.employee_id, attendance_date, attendance_date),
            )
            result = cur.fetchone()
            employee_key = result[0] if result else None

            def text_value(value):
                return None if pd.isna(value) else str(value)

            def number_value(value):
                return None if pd.isna(value) else value

            cur.execute(
                """
                INSERT INTO dw.fact_attendance (
                    attendance_id, employee_id, employee_key, date_key,
                    department_id, status, leave_type_code, check_in,
                    check_out, hours_worked, overtime_hours, late_flag,
                    source, data_quality_flag
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (attendance_id) DO UPDATE SET
                    employee_key = EXCLUDED.employee_key,
                    date_key = EXCLUDED.date_key,
                    department_id = EXCLUDED.department_id,
                    status = EXCLUDED.status,
                    leave_type_code = EXCLUDED.leave_type_code,
                    check_in = EXCLUDED.check_in,
                    check_out = EXCLUDED.check_out,
                    hours_worked = EXCLUDED.hours_worked,
                    overtime_hours = EXCLUDED.overtime_hours,
                    late_flag = EXCLUDED.late_flag,
                    source = EXCLUDED.source,
                    data_quality_flag = EXCLUDED.data_quality_flag
                """,
                (
                    str(row.attendance_id),
                    row.employee_id,
                    employee_key,
                    date_key,
                    text_value(row.department_id),
                    text_value(row.status),
                    text_value(row.leave_type_code),
                    text_value(row.check_in),
                    text_value(row.check_out),
                    number_value(row.hours_worked),
                    number_value(row.overtime_hours),
                    1 if str(row.late_flag).strip().upper() == "Y" else 0,
                    text_value(row.source),
                    text_value(row.data_quality_flag),
                ),
            )

print(f"Loaded {len(daily_attendance)} daily attendance rows.")

# Load AI/ML anomaly sample
ANOMALY_FILE = "data/raw/03_PulseIQ_Analytics_Star_Schema_Dataset.xlsx"

anomalies = pd.read_excel(ANOMALY_FILE, sheet_name="fact_anomaly")
anomalies["period"] = pd.to_datetime(anomalies["period"]).dt.date
anomalies["scored_at"] = pd.to_datetime(anomalies["scored_at"], utc=True).dt.tz_localize(None)

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        for row in anomalies.itertuples(index=False, name=None):
            cur.execute(
                """
                INSERT INTO dw.fact_anomaly (
                    result_id, source_dataset, record_id, employee_id,
                    period, anomaly_score, flagged, reason_code, reason_text,
                    money_at_risk, model_version, scored_at, period_key
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (result_id) DO UPDATE SET
                    flagged = EXCLUDED.flagged,
                    anomaly_score = EXCLUDED.anomaly_score,
                    reason_text = EXCLUDED.reason_text
                """,
                tuple(None if pd.isna(v) else v for v in row),
            )

print(f"Loaded {len(anomalies)} anomaly rows.")
