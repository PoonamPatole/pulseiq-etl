
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
WORKBOOK = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "03_PulseIQ_Analytics_Star_Schema_Dataset.xlsx"
)

invoices = pd.read_excel(
    WORKBOOK,
    sheet_name="fact_invoice",
    nrows=5,
)

print("INVOICE COLUMNS:")
print(invoices.columns.tolist())
print("\nFIRST FIVE ROWS:")
print(invoices.head().to_string(index=False))
