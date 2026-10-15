-- 1. Monthly attendance rate
SELECT
    DATE_TRUNC('month', full_date)::date AS month,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE status IN ('PRESENT', 'WFH')
        ) / NULLIF(COUNT(*), 0),
        1
    ) AS attendance_rate_pct
FROM dw.fact_attendance a
JOIN dw.dim_date d ON a.date_key = d.date_key
GROUP BY 1
ORDER BY 1;

-- 2. Attendance rate by department
SELECT
    department_id,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE status IN ('PRESENT', 'WFH')
        ) / NULLIF(COUNT(*), 0),
        1
    ) AS attendance_rate_pct
FROM dw.fact_attendance
GROUP BY department_id
ORDER BY attendance_rate_pct;

-- 3. Attendance by weekday
SELECT
    TO_CHAR(d.full_date, 'Day') AS weekday,
    EXTRACT(ISODOW FROM d.full_date) AS weekday_number,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE a.status IN ('PRESENT', 'WFH')
        ) / NULLIF(COUNT(*), 0),
        1
    ) AS attendance_rate_pct
FROM dw.fact_attendance a
JOIN dw.dim_date d ON a.date_key = d.date_key
GROUP BY 1, 2
ORDER BY 2;

-- 4. Leave days by type
SELECT
    leave_type_code,
    SUM(days) AS leave_days
FROM dw.fact_leave
WHERE status = 'Approved'
GROUP BY leave_type_code
ORDER BY leave_days DESC;

-- 5. Late arrivals by month
SELECT
    DATE_TRUNC('month', d.full_date)::date AS month,
    SUM(a.late_flag) AS late_arrivals
FROM dw.fact_attendance a
JOIN dw.dim_date d ON a.date_key = d.date_key
GROUP BY 1
ORDER BY 1;

SELECT status, COUNT(*)
FROM dw.fact_leave
GROUP BY status
ORDER BY status;

SELECT
    month,
    attendance_rate_pct,
    ROUND(
        AVG(attendance_rate_pct) OVER (
            ORDER BY month
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ),
        2
    ) AS rolling_3_month_avg
FROM (
    SELECT
        DATE_TRUNC('month', d.full_date)::date AS month,
        100.0 * COUNT(*) FILTER (
            WHERE a.status IN ('PRESENT', 'WFH')
        ) / NULLIF(COUNT(*), 0) AS attendance_rate_pct
    FROM dw.fact_attendance a
    JOIN dw.dim_date d ON a.date_key = d.date_key
    GROUP BY 1
) monthly
ORDER BY month;
