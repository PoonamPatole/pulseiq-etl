from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
WORKBOOK = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "03_PulseIQ_Analytics_Star_Schema_Dataset.xlsx"
)

issues = pd.read_excel(
    WORKBOOK,
    sheet_name="dq_known_issues",
)

print("Known-issues columns:")
print(issues.columns.tolist())

print("\nKnown-issues documentation:")
print(issues.to_string(index=False))
