from typing import Dict, Tuple, Set
import pandas as pd
from url_validator import validate_and_convert_url


def check_cross_team_email_duplicates(valid_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Scans all email columns (primary lead + member emails) across all rows to flag 
    duplicate candidate or member registrations across teams.
    
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (clean_valid_df, duplicate_failed_df)
    """
    if valid_df is None or not isinstance(valid_df, pd.DataFrame) or valid_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    df_work = valid_df.copy()
    
    # Target all columns containing 'email' (e.g., email, member_2_email, member_3_email)
    email_columns = [col for col in df_work.columns if "email" in str(col).lower()]

    # Map each clean email address to every row index where it appears
    email_to_rows: Dict[str, list] = {}

    for idx, row in df_work.iterrows():
        for col in email_columns:
            email_val = row.get(col)
            if email_val and isinstance(email_val, str) and email_val.strip():
                clean_email = email_val.strip().lower()
                if clean_email not in email_to_rows:
                    email_to_rows[clean_email] = []
                email_to_rows[clean_email].append(idx)

    # Identify row indices where an email appears in more than one submission
    duplicate_indices: Set[int] = set()
    row_reasons: Dict[int, str] = {}

    for email_val, row_indices in email_to_rows.items():
        unique_rows = set(row_indices)
        if len(unique_rows) > 1:
            for r_idx in unique_rows:
                duplicate_indices.add(r_idx)
                row_reasons[r_idx] = f"Duplicate email '{email_val}' registered across multiple teams."

    # Separate non-duplicate rows from conflicting duplicate rows
    valid_mask = ~df_work.index.isin(duplicate_indices)

    clean_valid_df = df_work[valid_mask].copy()
    duplicate_failed_df = df_work[~valid_mask].copy()

    if not duplicate_failed_df.empty:
        duplicate_failed_df["processing_status"] = "FAILED"
        duplicate_failed_df["failure_reason"] = duplicate_failed_df.index.map(row_reasons)

    return clean_valid_df, duplicate_failed_df

def check_duplicate_resumes(valid_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Validates resume URLs, converts Google Drive links to standardized download URLs, 
    and segregates rows with duplicate resume links/files into failed_df.
    
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (clean_valid_df, duplicate_failed_df)
    """
    if valid_df is None or not isinstance(valid_df, pd.DataFrame) or valid_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    df_work = valid_df.copy()
    
    # Track standardized URLs to row indices
    url_to_rows: Dict[str, list] = {}
    row_failure_reasons: Dict[int, str] = {}
    invalid_url_indices: Set[int] = set()

    for idx, row in df_work.iterrows():
        raw_url = row.get("resume_url")
        
        # 1. Validate & convert raw link using url_validator.py
        result = validate_and_convert_url(str(raw_url) if raw_url else "")
        
        if not result["is_valid"]:
            invalid_url_indices.add(idx)
            row_failure_reasons[idx] = f"Invalid resume URL: {result['reason']}"
            continue

        standardized_url = result["download_url"]

        # Update row with the standardized direct-download URL
        df_work.at[idx, "resume_url"] = standardized_url

        # 2. Map standardized URL to index for duplicate detection
        if standardized_url not in url_to_rows:
            url_to_rows[standardized_url] = []
        url_to_rows[standardized_url].append(idx)

    # 3. Identify duplicate resume file usages across rows
    duplicate_indices: Set[int] = set()
    for std_url, row_indices in url_to_rows.items():
        if len(row_indices) > 1:
            for r_idx in row_indices:
                duplicate_indices.add(r_idx)
                row_failure_reasons[r_idx] = "Duplicate resume URL/file detected across submissions."

    all_failed_indices = invalid_url_indices.union(duplicate_indices)

    # Separate clean rows from failed/duplicate rows
    valid_mask = ~df_work.index.isin(all_failed_indices)
    clean_valid_df = df_work[valid_mask].copy()
    duplicate_failed_df = df_work[~valid_mask].copy()

    if not duplicate_failed_df.empty:
        duplicate_failed_df["processing_status"] = "FAILED"
        duplicate_failed_df["failure_reason"] = duplicate_failed_df.index.map(row_failure_reasons)

    return clean_valid_df, duplicate_failed_df