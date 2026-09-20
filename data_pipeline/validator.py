# import pandas as pd
# from typing import Any, Tuple, Dict, Optional
# import re
# from excel import load_excel_sheets
# #Columns Validating
# Required_Columns = {"team_name", "name", "email", "resume_url", "domain"}
# EMAIL_REGEX=re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

# def is_empty_value(val: Any) -> bool :
#     "checks if cell is empty"
#     if val is None or pd.isna(val):
#         return True
#     str_val = str(val).strip()
#     return len(str_val) == 0 or str_val.lower() == "nan"

# def check_missing_required_fields(row_dict: Dict[str, Any]) -> Tuple[bool,str]:
#     """
#     checks all mandatory fields and combines all missing field names
#      into a clear issue message for the failure_reason column
#     """
#     missing_fields =[]
#     for field in ["team_name", "name", "email", "resume_url", "domain"]:
#         if is_empty_value(row_dict.get(field)):
#             missing_fields.append(field)

#     if missing_fields:
#         reason = (f"Missing required fields: {', '.join(missing_fields)}")
#         return False, reason
#     return True, ""

# def is_valid_email_string(email_str: str) -> bool:
#     """Validates basic syntax using standard library regex."""
#     if not email_str or not isinstance(email_str, str):
#         return False
#     return bool(EMAIL_REGEX.match(email_str))


# def validate_all_row_emails(cleaned_dict: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
#     """
#     Validates and lowercases lead email and all present team member emails 
#     using pure Python regex.
#     """
#     updated_dict = cleaned_dict.copy()
    
#     # Target all keys containing 'email'
#     email_keys = [k for k in updated_dict.keys() if "email" in str(k).lower()]

#     for key in email_keys:
#         raw_val = updated_dict.get(key)

#         # Skip empty optional team member emails
#         if raw_val is None or str(raw_val).strip() == "":
#             continue

#         clean_email = str(raw_val).strip().lower()

#         if not is_valid_email_string(clean_email):
#             # If primary lead email fails, output exact requested failure reason
#             if key == "email":
#                 return False, updated_dict, "Email is not valid"
#             return False, updated_dict, f"Email is not valid ({key}: '{clean_email}')"

#         # Update row dictionary with normalized email
#         updated_dict[key] = clean_email

#     return True, updated_dict, ""

# def validate_candidate_row(row_dict: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
#     """Validates the candidate row. Standadizes the values and captures 
#     any issues directly into the failure _reason string"""
#     cleaned_dict ={}
#     #Standardize empty values across all columns 
#     for k ,v in row_dict.items():
#         if is_empty_value(v):
#             cleaned_dict[k] = None
#         else:
#             cleaned_dict[k]=str(v).strip()
#     #catch emtirely blank rows
#     if all(v is None for v in cleaned_dict.values()):
#         return False, cleaned_dict, "Row is compeletly empty"
#     try:
#         is_valid,reason = check_missing_required_fields(cleaned_dict)
#         if not is_valid:
#             return False, cleaned_dict, reason
#         return True, cleaned_dict, ""
#     except Exception as err:
#         return False, cleaned_dict, f"Row processing error: {str(err)}"


# def validate_dataframe(df: pd.DataFrame, sheet_name:str) -> Tuple[pd.DataFrame, pd.DataFrame]:
#     """Validates the dataset structure and individual rows.
#     populates 'processing_status' and 'failure_reason' columns dynamically"""
#     if df is None or not isinstance(df, pd.DataFrame):
#         raise TypeError("Input must be a valid Pandas DataFrame.")
#     df_work = df
#     #Inject sheet_name as domain if domain column is missing or empty
#     if sheet_name and str(sheet_name).strip():
#         clean_sheet_domain = str(sheet_name).strip()
#         print(clean_sheet_domain)
#         if "domain" not in df_work.columns or df_work["domain"].isnull().all():
#             df_work["domain"] = clean_sheet_domain
#     #Check header columns presence
#     missing_columns = Required_Columns - set(df_work.columns)
#     if missing_columns:
#         raise ValueError(f"Excel header is missing mandatory column(s) : {','.join(sorted(missing_columns))}")
#     valid_records = []
#     failed_records = []
#     for idx, row in df_work.iterrows():
#         row_dict = row.to_dict()
#         is_valid, processed_row, reason = validate_candidate_row(row_dict)
#         if is_valid:
#             processed_row["processing_status"]="PENDING"
#             processed_row["failure_reason"]=None
#             valid_records.append(processed_row)
#         else:
#             processed_row["processing_status"]="FAILED"
#             processed_row["failure_reason"]= reason
#             failed_records.append(processed_row)

#     output_columns = list(df_work.columns)
#     valid_df = (
#         pd.DataFrame(valid_records)
#         if valid_records
#         else pd.DataFrame(columns=output_columns)
#     )
#     failed_df=(
#         pd.DataFrame(failed_records)
#         if failed_records
#         else pd.DataFrame(columns=output_columns)
#     )
#     return valid_df , failed_df

# validator.py

import pandas as pd
from typing import Tuple, Dict, Any
import re

REQUIRED_COLUMNS = {"team_name", "name", "email", "resume_url", "domain"}
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def is_empty_value(val: Any) -> bool:
    """Checks if a cell value is empty, None, or NaN."""
    if val is None or pd.isna(val):
        return True
    str_val = str(val).strip()
    return len(str_val) == 0 or str_val.lower() == "nan"


def validate_candidate_row(row_dict: Dict[str, Any]) -> Tuple[bool, str]:
    """Validates missing required fields and email syntax for a single row."""
    cleaned_dict = {
        k: (None if is_empty_value(v) else str(v).strip())
        for k, v in row_dict.items()
    }

    # Catch entirely blank rows
    if all(v is None for v in cleaned_dict.values()):
        return False, "Row is completely empty"

    # Check missing required fields
    missing = [f for f in REQUIRED_COLUMNS if cleaned_dict.get(f) is None]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"

    # Validate primary email syntax
    email_val = cleaned_dict.get("email")
    if email_val and not EMAIL_REGEX.match(email_val):
        return False, f"Invalid primary email format: '{email_val}'"

    return True, ""


def validate_dataframe(df: pd.DataFrame, sheet_name: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Validates DataFrame structure, fills missing domains from sheet names,
    and segregates valid/failed rows while maintaining index integrity.
    """
    if df is None or not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a valid Pandas DataFrame.")

    df_work = df.copy()

    # 1. Inject sheet_name into missing/empty domain cells
    if sheet_name and str(sheet_name).strip():
        clean_domain = str(sheet_name).strip()
        if "domain" not in df_work.columns:
            df_work["domain"] = clean_domain
        else:
            df_work["domain"] = df_work["domain"].fillna(clean_domain)
            df_work["domain"] = df_work["domain"].apply(
                lambda x: clean_domain if is_empty_value(x) else str(x).strip()
            )

    # 2. Check header presence
    missing_cols = REQUIRED_COLUMNS - set(df_work.columns)
    if missing_cols:
        raise ValueError(f"Excel header missing mandatory column(s): {', '.join(sorted(missing_cols))}")

    # 3. Validate rows while preserving original DataFrame structure
    statuses = []
    reasons = []

    for _, row in df_work.iterrows():
        is_valid, reason = validate_candidate_row(row.to_dict())
        if is_valid:
            statuses.append("PENDING")
            reasons.append(None)
        else:
            statuses.append("FAILED")
            reasons.append(reason)

    df_work["processing_status"] = statuses
    df_work["failure_reason"] = reasons

    # Segregate without losing index or column metadata
    valid_df = df_work[df_work["processing_status"] == "PENDING"].copy()
    failed_df = df_work[df_work["processing_status"] == "FAILED"].copy()

    return valid_df, failed_df