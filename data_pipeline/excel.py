from typing import Dict, Tuple
from pathlib import Path
import shutil
import pandas as pd


def load_excel_sheets(
    file_name: str = "Original.xlsx",
    copy_name: str = "Working_Copy.xlsx"
) -> Tuple[bool, Dict[str, pd.DataFrame], str]:
    """
    Creates a working copy of the input Excel file and loads all sheets 
    into an in-memory dictionary mapping sheet names to DataFrames.

    Returns:
        Tuple[bool, sheets_dict, error_message]
    """
    try:
        base_dir = Path(__file__).resolve().parent
        input_dir = base_dir / "input"
        excel_path = input_dir / file_name
        copy_path = input_dir / copy_name

        # 1. Verify original file exists
        if not excel_path.exists():
            return False, {}, f"File not found: '{excel_path}'"

        # 2. Ensure input directory exists and create safe copy
        input_dir.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(excel_path, copy_path)
        except Exception as copy_err:
            return False, {}, f"Failed to create working copy: {str(copy_err)}"

        # 3. Read Excel file safely
        try:
            excel_file = pd.ExcelFile(copy_path)
        except Exception as read_err:
            return False, {}, f"Invalid or corrupted Excel file: {str(read_err)}"

        if not excel_file.sheet_names:
            return False, {}, "Excel file contains no sheet tabs."

        # 4. Extract all sheets into a dictionary
        sheets_dict: Dict[str, pd.DataFrame] = {}
        for sheet_name in excel_file.sheet_names:
            try:
                sheet_df = pd.read_excel(excel_file, sheet_name=sheet_name)
                # Skip completely empty sheets
                if sheet_df is not None and not sheet_df.empty and not sheet_df.dropna(how="all").empty:
                    sheets_dict[sheet_name] = sheet_df
            except Exception:
                print (f"Error reading sheet {sheet_name}")

        if not sheets_dict:
            return False, {}, "All sheets in the workbook are empty or unreadable."

        return True, sheets_dict, ""

    except Exception as err:
        return False, {}, f"Unexpected error loading Excel file: {str(err)}"


load_excel_sheets()

