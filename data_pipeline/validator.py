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