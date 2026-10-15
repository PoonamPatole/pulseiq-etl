CREATE SCHEMA IF NOT EXISTS dw;

CREATE TABLE IF NOT EXISTS dw.dim_employee (
    employee_key BIGINT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    full_name TEXT,
    gender TEXT,
    date_of_birth DATE,
    hire_date DATE,
    exit_date DATE,
    employment_status TEXT,
    employment_type TEXT,
    department_id TEXT,
    role_id TEXT,
    role_title TEXT,
    job_level TEXT,
    manager_id TEXT,
    work_location TEXT,
    work_mode TEXT,
    highest_education TEXT,
    valid_from DATE NOT NULL,
    valid_to DATE,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    change_reason TEXT,
    UNIQUE (employee_id, valid_from)
);

CREATE TABLE IF NOT EXISTS dw.fact_payroll (
    payroll_item_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    employee_id TEXT NOT NULL,
    date_key INTEGER,
    employee_key BIGINT REFERENCES dw.dim_employee(employee_key),
    period_end_date DATE,
    department_id TEXT,
    role_id TEXT,
    payable_days NUMERIC,
    lop_days NUMERIC,
    overtime_hours_paid NUMERIC,
    variable_pay_type TEXT,
    monthly_fixed_gross NUMERIC(14,2),
    basic NUMERIC(14,2),
    hra NUMERIC(14,2),
    conveyance NUMERIC(14,2),
    medical NUMERIC(14,2),
    special_allowance NUMERIC(14,2),
    earned_fixed_pay NUMERIC(14,2),
    overtime_pay NUMERIC(14,2),
    variable_pay NUMERIC(14,2),
    gross_pay NUMERIC(14,2),
    pf_employee NUMERIC(14,2),
    esi_employee NUMERIC(14,2),
    professional_tax NUMERIC(14,2),
    tds NUMERIC(14,2),
    other_deductions NUMERIC(14,2),
    total_deductions NUMERIC(14,2),
    net_pay NUMERIC(14,2),
    pf_employer NUMERIC(14,2),
    esi_employer NUMERIC(14,2),
    employer_cost NUMERIC(14,2),
    headcount_flag INTEGER
);

CREATE INDEX IF NOT EXISTS idx_payroll_run
    ON dw.fact_payroll(run_id);

CREATE INDEX IF NOT EXISTS idx_payroll_employee
    ON dw.fact_payroll(employee_key);

CREATE INDEX IF NOT EXISTS idx_payroll_period
    ON dw.fact_payroll(period_end_date);


CREATE TABLE IF NOT EXISTS dw.dim_department (
    department_id TEXT PRIMARY KEY,
    department_name TEXT,
    cost_center TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS dw.dim_role (
    role_id TEXT PRIMARY KEY,
    department_id TEXT,
    role_title TEXT,
    level INTEGER,
    grade TEXT,
    band_min_annual NUMERIC(14,2),
    band_mid_annual NUMERIC(14,2),
    band_max_annual NUMERIC(14,2),
    overtime_eligible TEXT,
    band_year INTEGER
);

CREATE TABLE IF NOT EXISTS dw.dim_leave_type (
    leave_type_code TEXT PRIMARY KEY,
    leave_type_name TEXT,
    pay_type TEXT,
    annual_quota_days NUMERIC,
    prorated_for_joiners TEXT,
    carry_forward_allowed TEXT,
    max_carry_forward_days INTEGER,
    policy_note TEXT
);

CREATE TABLE IF NOT EXISTS dw.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE UNIQUE NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS dw.fact_attendance_monthly (
    attendance_fact_id BIGSERIAL PRIMARY KEY,
    employee_id TEXT NOT NULL,
    employee_key BIGINT REFERENCES dw.dim_employee(employee_key),
    date_key INTEGER REFERENCES dw.dim_date(date_key),
    department_id TEXT,
    scheduled_days NUMERIC,
    present_days NUMERIC,
    wfh_days NUMERIC,
    half_days_unpaid NUMERIC,
    paid_leave_days NUMERIC,
    unpaid_absence_days NUMERIC,
    late_arrivals INTEGER,
    avg_hours_worked NUMERIC,
    overtime_hours NUMERIC,
    attendance_rate NUMERIC,
    period_end_date DATE,
    UNIQUE (employee_id, period_end_date)
);

CREATE TABLE IF NOT EXISTS dw.fact_leave (
    leave_request_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    employee_key BIGINT REFERENCES dw.dim_employee(employee_key),
    leave_type_code TEXT REFERENCES dw.dim_leave_type(leave_type_code),
    start_date_key INTEGER REFERENCES dw.dim_date(date_key),
    end_date_key INTEGER REFERENCES dw.dim_date(date_key),
    start_date DATE,
    end_date DATE,
    days NUMERIC,
    status TEXT,
    applied_on DATE,
    decided_on DATE,
    approver_id TEXT,
    reason TEXT
);

CREATE TABLE IF NOT EXISTS dw.fact_headcount_monthly (
    department_id TEXT NOT NULL,
    month DATE NOT NULL,
    headcount_end INTEGER,
    hires INTEGER,
    exits INTEGER,
    attrition_rate_monthly_pct NUMERIC,
    PRIMARY KEY (department_id, month)
);

CREATE INDEX IF NOT EXISTS idx_attendance_employee
    ON dw.fact_attendance_monthly(employee_key);

CREATE INDEX IF NOT EXISTS idx_attendance_period
    ON dw.fact_attendance_monthly(period_end_date);

CREATE INDEX IF NOT EXISTS idx_leave_employee
    ON dw.fact_leave(employee_key);

CREATE INDEX IF NOT EXISTS idx_leave_dates
    ON dw.fact_leave(start_date, end_date);


CREATE TABLE IF NOT EXISTS dw.fact_attendance (
    attendance_id TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    employee_key BIGINT REFERENCES dw.dim_employee(employee_key),
    date_key INTEGER REFERENCES dw.dim_date(date_key),
    department_id TEXT,
    status TEXT,
    leave_type_code TEXT,
    check_in TEXT,
    check_out TEXT,
    hours_worked NUMERIC,
    overtime_hours NUMERIC,
    late_flag INTEGER,
    source TEXT,
    data_quality_flag TEXT
);

CREATE INDEX IF NOT EXISTS idx_attendance_daily_employee
    ON dw.fact_attendance(employee_key);

CREATE INDEX IF NOT EXISTS idx_attendance_daily_date
    ON dw.fact_attendance(date_key);

CREATE INDEX IF NOT EXISTS idx_attendance_daily_department
    ON dw.fact_attendance(department_id);
