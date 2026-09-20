import pandas as pd
from typing import Tuple, List, Dict, Any
from excel import load_excel_sheets
from normalizer import normalize_columns, normalize_all_emails
from validator import validate_dataframe
from url_validator import process_resume_urls
from deduplicator import check_cross_team_email_duplicates, check_duplicate_resumes
from resume_downloader import download_resume_in_memory


def run_pipeline() -> Tuple[pd.DataFrame, pd.DataFrame, List[Dict[str, Any]]]:
    """
    Executes the sequential ATS candidate pipeline across all Excel sheets.
    
    Flow:
    1. Excel -> Load sheets
    2. Normalizer -> Clean column headers & emails
    3. Validator -> Row validation & missing field checks (Sets PENDING/FAILED)
    4. URL Validator -> Verify URLs and apply SSRF protection for PENDING rows
    5. Deduplicator -> Check cross-team email & duplicate resume URLs
    6. Resume Downloader -> Fetch resume text in-memory for surviving PENDING candidates
    """
    master_valid_dfs: List[pd.DataFrame] = []
    master_failed_dfs: List[pd.DataFrame] = []

    # 1. Excel Ingestion
    success, sheets_dict, err = load_excel_sheets("Original.xlsx")
    if not success:
        print(f"[CRITICAL ERROR] Excel loading failed: {err}")
        return pd.DataFrame(), pd.DataFrame(), []

    print(f"Loaded {len(sheets_dict)} sheet(s) for processing.")

    # Process each domain/sheet tab
    for sheet_name, raw_df in sheets_dict.items():
        print(f"\n--- Processing Sheet: {sheet_name} ---")
        print("Original Excel columns:",[repr(c) for c in raw_df.columns])
        # 2. Normalization
        norm_success, norm_df, norm_err = normalize_columns(raw_df)
        print("Normalized columns:",list(norm_df.columns))
        if not norm_success:
            print(f"Skipping sheet '{sheet_name}': {norm_err}")
            continue

        norm_df = normalize_all_emails(norm_df)

        # 3. Row-Level Validation
        try:
            valid_df, step1_failed_df = validate_dataframe(norm_df, sheet_name=sheet_name)
            if not step1_failed_df.empty:
                master_failed_dfs.append(step1_failed_df)
        except Exception as val_err:
            print(f"Validation error on sheet '{sheet_name}': {val_err}")
            continue

        if valid_df.empty:
            print(f"No valid records in sheet '{sheet_name}' after initial validation.")
            continue

        # 4. URL Validation (Runs only on PENDING rows from validator)
        pending_url_df = valid_df[valid_df["processing_status"] == "PENDING"].copy()
        valid_df, step2_failed_df = process_resume_urls(pending_url_df)
        if not step2_failed_df.empty:
            master_failed_dfs.append(step2_failed_df)

        if valid_df.empty:
            continue

        master_valid_dfs.append(valid_df)

    # Combine valid records across all sheets prior to cross-team deduplication
    if not master_valid_dfs:
        print("\nNo candidate rows passed validation.")
        combined_failed_df = pd.concat(master_failed_dfs, ignore_index=True) if master_failed_dfs else pd.DataFrame()
        return pd.DataFrame(), combined_failed_df, []

    combined_valid_df = pd.concat(master_valid_dfs, ignore_index=True)

    # 5. Cross-Team Deduplication (Runs on combined PENDING rows)
    # 5a. Check cross-team email duplicates
    combined_valid_df, email_failed_df = check_cross_team_email_duplicates(combined_valid_df)
    if not email_failed_df.empty:
        master_failed_dfs.append(email_failed_df)

    # 5b. Check duplicate resume links/files
    final_valid_df, resume_failed_df = check_duplicate_resumes(combined_valid_df)
    if not resume_failed_df.empty:
        master_failed_dfs.append(resume_failed_df)

    # Master failure consolidation
    final_failed_df = pd.concat(master_failed_dfs, ignore_index=True) if master_failed_dfs else pd.DataFrame()

    # 6. Resume Downloader (Only processes surviving PENDING rows)
    download_results = []
    pending_download_df = final_valid_df[final_valid_df["processing_status"] == "PENDING"]

    print(f"\nStarting resume downloads for {len(pending_download_df)} valid candidate(s)...")

    for idx, row in pending_download_df.iterrows():
        candidate_name = row.get("Lead_name") or row.get("name") or f"Candidate_{idx}"
        resume_url = row.get("resume_url")

        print(f"Downloading resume for: {candidate_name}")
        dl_result = download_resume_in_memory(resume_url)
        
        download_results.append({
            "candidate_index": idx,
            "candidate_name": candidate_name,
            "resume_url": resume_url,
            "download_success": dl_result["success"],
            "resume_text": dl_result.get("resume_text", ""),
            "download_reason": dl_result.get("reason")
        })

    return final_valid_df, final_failed_df, download_results


if __name__ == "__main__":
    valid_df, failed_df, downloaded_resumes = run_pipeline()

    print("\n================ PIPELINE SUMMARY ================")
    print(f"Total Valid Candidates Queued: {len(valid_df)}")
    print(f"Total Failed Candidates Logged: {len(failed_df)}")
    print(f"Total Resumes Processed in Memory: {len(downloaded_resumes)}")