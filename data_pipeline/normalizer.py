import pandas as pd
import re
from typing import Any, Tuple, Union, Dict,Optional

COLUMN_ALIASES= {
    #Team Name
    # Candidate Name
    "Team Name": "team_name",
    "Team name": "team_name",
    "team name": "team_name",
    "team_name" : "team_name",
    
    #Team lead name
    "candidate name": "name",
    "student name": "name",
    "full name": "name",
    "applicant name": "name",
    "member 1 name":"name",
    "Member 1 name": "name",
    "Lead name":"name",
    "Leader name": "name",
    "name": "name",
    "Member 1 Name (Team Lead)":"name",
    #Member 2 name
    "Member 2": "member_2_name",
    "member 2 name":"member_2_name",
    "Team member 2":"member_2_name",
    "team member 2": "member_2_name",
    "second member": "member_2_name",
    "teammate 1": "member_2_name",
    "partner name": "member_2_name",
    "Member 2 Name":"member_2_name",
    #Member 3
    "member 3": "member_3_name",
    "member 3 name": "member_3_name",
    "team member 3": "member_3_name",
    "third member": "member_3_name",
    "teammate 2": "member_3_name",
    "Member 3 Name":"member_3_name",
     #Member 4
    "member 4": "member_4_name",
    "member 4 name": "member_4_name",
    "team member 4": "member_4_name",
    "fourth member": "member_4_name",
    "teammate 3": "member_4_name",
    "Member 4 Name":"member_4_name",
    # Email
    "email address": "email",
    "email id": "email",
    "e-mail": "email",
    "mail id": "email",
    "email": "email",
    "Member 1 email":"email",
    "member 1 email":"email",
    "Team leader email":"email",
    "team lead email":"email",
    "Member 1 Email":"email",
    # Member 2 Email
    "member 2 email": "member_2_email",
    "member 2 email id": "member_2_email",
    "teammate 1 email": "member_2_email",
    "partner email": "member_2_email",
    "Member 2 Email":"member_2_email",    
    # Member 3 Email
    "member 3 email": "member_3_email",
    "member 3 email id": "member_3_email",
    "teammate 2 email": "member_3_email",
    "Member 3 Email":"member_3_email",
    # Member 4 Email
    "member 4 email": "member_4_email",
    "member 4 email id": "member_4_email",
    "teammate 3 email": "member_4_email",
    "Member 4 Email":"member_4_email",
    # Resume Links
    "resume link": "resume_url",
    "member 1 resume":"resume_url",
    "resume url": "resume_url",
    "drive link": "resume_url",
    "google drive link": "resume_url",
    "resume": "resume_url",
    "cv link": "resume_url",
    "url": "resume_url",
    "link": "resume_url",
    "Member 1 Resume":"resume_url",
    "Team Lead Resume":"resume_url",
    "Leader Resume":"resume_url",
    # Domain
    "domain": "domain",
    "branch": "domain",
    "field": "domain",
    "track": "domain",
    # Optional Fields
    "college name": "college",
    "college": "college",
    "university": "college",
    "phone number": "phone",
    "mobile number": "phone",
    "contact number": "phone",
    "phone": "phone",
    "github link": "github",
    "github profile": "github",
    "github": "github",
    "linkedin link": "linkedin",
    "linkedin profile": "linkedin",
    "linkedin": "linkedin",
}
#checks the column name in proper format
def clean_header_string(header: Any) -> str:
    """Strips quotes, parenthetical notes, special characters, and normalizes spacing."""
    if header is None or pd.isna(header):
        return ""
    
    h_str = str(header).replace("\xa0", " ").strip()
    h_str = str(header).strip()
    
    # Strip literal double/single quotes from string ends
    h_str = h_str.strip('"' + "'")
    
    # Lowercase
    h_str = h_str.lower()
    
    # Remove text inside parentheses e.g. "(team lead)" -> ""
    h_str = re.sub(r"\(.*?\)", "", h_str)
    
    # Convert multiple spaces, underscores, and hyphens into a single space
    h_str = re.sub(r"[\s_\-]+", " ", h_str).strip()
    return h_str

def clean_email_value(val: str) -> Optional[str]:
    """Strips whitespace and converts email to lowercase."""
    if val is None or pd.isna(val):
        return None
    email_str = str(val).strip().lower()
    if not email_str or email_str == "nan":
        return None
    return email_str

def normalize_all_emails(df: pd.DataFrame) -> pd.DataFrame:
    """Normalizes all primary and team member email columns in the DataFrame."""
    df_normalized_emails = df
    email_columns = [col for col in df_normalized_emails.columns if isinstance(col,str) and "email" in col.lower()]

    for col in email_columns:
        df_normalized_emails[col] = df_normalized_emails[col].apply(clean_email_value)
    return df_normalized_emails

def normalize_columns(df: pd.DataFrame) -> Tuple[bool, pd.DataFrame, str]:
    """
    Normalizes DataFrame headers using the alias dictionary.
    Returns (success, normalized_df, error_message).
    """
    # if df is None or not isinstance(df, pd.DataFrame):
    #     return False, pd.DataFrame(), "Invalid input: expected a Pandas DataFrame."

    if df.empty:
        return False, df, "DataFrame is completely empty."

    try:
        df_normalized = df
        # 1. Clean each column and replace with its alias in one pass
        df_normalized.columns = [
            COLUMN_ALIASES.get(clean_header_string(col), clean_header_string(col))
            for col in df_normalized.columns
        ]
        return True, df_normalized, ""
    except Exception as err:
            return False, df, f"Failed during column renaming: {(err)}"