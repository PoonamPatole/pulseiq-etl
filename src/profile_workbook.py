
from pathlib import Path
import pandas as pd

project_dir = Path(__file__).resolve().parent.parent

workbook = (
    project_dir
    / "data"
    / "raw"
    / "03_PulseIQ_Analytics_Star_Schema_Dataset.xlsx"
)

output_file = project_dir / "workbook_profile.txt"

if not workbook.exists():
    raise FileNotFoundError(f"Workbook not found: {workbook}")

with pd.ExcelFile(workbook) as excel:
    with output_file.open("w", encoding="utf-8") as report:
        for sheet in excel.sheet_names:
            df = pd.read_excel(excel, sheet_name=sheet, nrows=0)
            row_count = len(
                pd.read_excel(excel, sheet_name=sheet, usecols=[0])
            )

            report.write(f"\nSHEET: {sheet}\n")
            report.write(f"Rows: {row_count}\n")
            report.write(
                "Columns: " + ", ".join(map(str, df.columns)) + "\n"
            )

print(f"Workbook profile saved to: {output_file}")
print("Only sheet names, row counts, and column names were recorded.")
