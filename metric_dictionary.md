# PulseIQ — Metric Dictionary

## Purpose
Document the business metrics used by the PulseIQ analytics ETL project.

**Source workbook:** `03_PulseIQ_Analytics_Star_Schema_Dataset.xlsx`

**Authoritative source:** `metric_dictionary` worksheet.

## Official Metric Definitions

| Metric | Business definition | Formula | Source table | Grain / period |
|---|---|---|---|---|
| Headcount | Active permanent and contract employees on the last day of the month. | `COUNT(DISTINCT employee_id)` where `hire_date <= month_end` and (`exit_date IS NULL` or `exit_date > month_end`) | `fact_headcount_monthly` / `dim_employee` | Department × month; month-end |
| Hires | Employees whose hire date falls within the month. Transfers are not hires. | `COUNT(employee_id)` where hire date falls within the month | `fact_headcount_monthly` | Department × month |
| Exits | Employees whose exit date falls within the month, including resignations, terminations, and contract endings. | `COUNT(employee_id)` where exit date falls within the month | `fact_headcount_monthly` | Department × month |
| Attrition rate (monthly) | Share of people who left during the month. | `Exits / headcount_start * 100` | `fact_headcount_monthly` | Department × month |
| Attrition rate (rolling 12 months) | Leavers in the last 12 months divided by average headcount over the same months. | `SUM(exits, 12m) / AVG(headcount_end, 12m) * 100` | `fact_headcount_monthly` | Department × rolling 12 months |
| Gross Pay | Total earnings before deductions for the month, including overtime and variable pay. | `SUM(gross_pay)` | `fact_payroll` | Employee × month |
| Net Pay | Take-home pay after employee deductions. | `SUM(net_pay)` | `fact_payroll` | Employee × month |
| Payroll Cost (Employer Cost) | Full cost of employees to the company: gross pay plus employer PF and ESI. | `SUM(employer_cost)` | `fact_payroll` | Employee × month |
| Payroll as % of Revenue | Share of revenue consumed by payroll cost. | `Payroll cost / Revenue * 100` | `fact_payroll` + `fact_ledger` | Month |



## Reporting Notes

- Monthly attrition can be noisy for small departments. The workbook recommends a minimum group size of 10 for attrition rates.
- The workbook specifies a minimum group size of 5 for headcount, hires, and exits.
- Rolling 12-month attrition is recommended for headline reporting.
- The headcount definition excludes the CEO when comparing departments only.
- Use the workbook's `metric_dictionary` sheet to verify any additional metrics before documenting them.
- Do not silently change source figures to make reconciliation pass. Record differences for investigation.

## Data Quality Status

Payroll reconciliation currently reports 17 months as `PASS` and one month, June 2026, as `REVIEW`. The June difference is ₹-18,450.00 and remains unresolved.

**Document status:** Draft. Some metric definitions have been verified against the official workbook; remaining metrics and payroll definitions still require verification.
