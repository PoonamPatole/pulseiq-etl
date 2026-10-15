# PulseIQ Dashboard Design Notes

## AI design prompt

Design a clean, professional Headcount & Departments dashboard for PulseIQ People Analytics.

Follow the PulseIQ style guide:
- Navy `#1F3864`, blue `#2E75B6`, orange `#C55A11`, green `#548235`, and grey `#7F7F7F`.
- Use Arial or Inter.
- Place four KPI tiles at the top.
- Place headcount trend and department comparison charts below.
- Include tenure bands, role mix, and joiners-versus-leavers charts.
- Add department and date-range filters.
- Every chart must have a clear title and a one-line takeaway.
- Prefer bar and line charts. Avoid 3D charts and crowded pie charts.
- Use readable layouts for laptop and mobile screens.
- Do not invent business data; use actual warehouse values.

## Design review and improvements

- Put current headcount first because it is the main dashboard metric.
- Use the required PulseIQ colour palette.
- Prefer bar charts for department and role comparisons.
- Use a line chart for the headcount trend.
- Include department and date-range filters.
- Add one-line takeaways based on actual warehouse numbers.
- Verify dashboard numbers against PostgreSQL before publishing.

## Data integrity

The AI-generated design is a layout reference only. Example numbers in the mockup are not verified business results and must not be used in the final dashboard.

## Chart takeaways

- Current Headcount: 441 active employees are currently recorded in the warehouse.
- Headcount Trend: Review monthly headcount changes over time.
- Headcount by Department: Compare department headcount to identify the largest teams.
- Tenure Bands: Most active employees fall within the 1–3 year tenure band (123 employees).
- Role Mix: Compare active employee counts across job roles.
- Joiners vs Leavers: Compare monthly hires and exits to understand workforce movement.
