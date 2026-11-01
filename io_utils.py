"""Reading tabular inputs (CSV or a sheet of the Data S1 workbook)."""
from pathlib import Path

import pandas as pd


def read_table(path, sheet=None):
    if Path(path).suffix.lower() in (".xlsx", ".xls"):
        if sheet is None:
            raise SystemExit(f"{path} is a workbook: give the sheet with --sheet "
                             f"(available: {', '.join(pd.ExcelFile(path).sheet_names)})")
        return pd.read_excel(path, sheet_name=sheet)
    return pd.read_csv(path)
