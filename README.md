# PulseIQ — Workforce Analytics & ETL

## Project Overview

PulseIQ is a workforce analytics project that cleans data, loads a PostgreSQL analytics warehouse, and builds dashboards for headcount, departments, attendance, and leave.

## Completed Tasks

### Task 1 — ETL Pipeline
- Cleaned employee and payroll data using Python and Pandas.
- Generated clean CSV and Parquet files.
- Added data-quality validation and rejected-row outputs.
- Verified the pipeline with automated tests.

### Task 2 — Analytics Warehouse
- Created a PostgreSQL data warehouse using a star schema.
- Loaded employee, payroll, attendance, leave, and dimension data.
- Implemented upserts and employee history tracking.
- Checked key results against the reference data.

### Task 3 — Headcount & Departments Dashboard
- Built a dashboard in Apache Superset.
- Included current headcount, headcount trends, department distribution, tenure bands, role mix, and joiners versus leavers.
- Added dashboard filters and documented the design decisions.
- Saved the dashboard export under `dashboards/`.

### Task 4 — Attendance & Leave Analysis
- Analysed monthly attendance, department and weekday trends, leave types, and late arrivals.
- Calculated rolling averages.
- Loaded the sample AI anomaly data.
- Built the Attendance & Leave dashboard and documented findings and limitations.

## Project Structure

- `data/raw/` — Source workbooks
- `data/clean/` — Cleaned data files
- `src/` — Python pipeline and warehouse loader
- `tests/` — Automated tests
- `sql/` — Warehouse and analysis SQL
- `docs/` — Project documentation and design notes
- `dashboards/` — Dashboard exports
- `logs/` — Pipeline logs

## Technologies Used

Python, Pandas, Pandera, PostgreSQL, Docker Compose, Apache Superset, SQL, Pytest, CSV, and Parquet.

## Run Locally

Run these commands from the project root:

```powershell
python -m pytest tests/ -v
python -m src.pipeline
```

To start the database and Superset services:

```powershell
docker compose up -d db superset
```

To load the warehouse:

```powershell
python -m src.load_warehouse
```

## Dashboard Access

- Local Superset: http://localhost:8088
- Dashboard exports: `dashboards/`

## Assumptions and Limitations

- The supplied datasets may be synthetic and do not establish real-world causes.
- AI anomaly flags are signals for investigation, not proof of an error.
- Flagged anomaly dates are shown separately; individual anomaly markers are not overlaid on the attendance trend line.
- Department sizes differ, and late-arrival counts are not adjusted for headcount.

## Handoff Package

- Warehouse schema: `docs/warehouse-schema.md`
- Dashboard design notes: `docs/design-notes.md`
- Attendance insights: `docs/attendance-insights.md`
- Warehouse SQL: `sql/warehouse.sql`
- Attendance analysis SQL: `sql/attendance_analysis.sql`
- Dashboard exports: `dashboards/`

## Status

Tasks 1–4 are completed. Tasks beyond Task 4 are not claimed as completed.
