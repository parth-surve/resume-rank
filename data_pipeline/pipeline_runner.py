import pandas as pd

from typing import Tuple, List, Dict, Any

from data_pipeline.excel import load_excel_sheets
from data_pipeline.normalizer import normalize_columns, normalize_all_emails
from data_pipeline.validator import validate_dataframe
from data_pipeline.url_validator import process_resume_urls
from data_pipeline.deduplicator import (
    check_cross_team_email_duplicates,
    check_duplicate_resumes,
)
from data_pipeline.resume_downloader import download_resume_in_memory
from data_pipeline.resume_parser import parse_resume

def run_pipeline(
    file_path: str,
) -> Tuple[pd.DataFrame, pd.DataFrame, List[Dict[str, Any]]]:
    """
    Executes the sequential ATS candidate pipeline across all Excel sheets.

    Flow:

    1. Excel -> Load sheets
    2. Normalizer -> Clean column headers & emails
    3. Validator -> Row validation & missing field checks
    4. URL Validator -> Verify URLs and apply SSRF protection
    5. Deduplicator -> Check cross-team email & duplicate resume URLs
    6. Resume Downloader -> Fetch resume text in-memory
    """

    master_valid_dfs: List[pd.DataFrame] = []
    master_failed_dfs: List[pd.DataFrame] = []

    # 1. Excel Ingestion
    success, sheets_dict, err = load_excel_sheets(file_path)

    if not success:
        print(f"[CRITICAL ERROR] Excel loading failed: {err}")
        return pd.DataFrame(), pd.DataFrame(), []

    print(f"Loaded {len(sheets_dict)} sheet(s) for processing.")

    # Process each domain/sheet tab
    for sheet_name, raw_df in sheets_dict.items():
        print(f"\n--- Processing Sheet: {sheet_name} ---")
        print(
            "Original Excel columns:",
            [repr(c) for c in raw_df.columns],
        )

        # 2. Normalization
        norm_success, norm_df, norm_err = normalize_columns(raw_df)

        print("Normalized columns:", list(norm_df.columns))

        if not norm_success:
            print(f"Skipping sheet '{sheet_name}': {norm_err}")
            continue

        norm_df = normalize_all_emails(norm_df)

        # 3. Row-Level Validation
        try:
            valid_df, step1_failed_df = validate_dataframe(
                norm_df,
                sheet_name=sheet_name,
            )

            if not step1_failed_df.empty:
                master_failed_dfs.append(step1_failed_df)

        except Exception as val_err:
            print(
                f"Validation error on sheet '{sheet_name}': {val_err}"
            )
            continue

        if valid_df.empty:
            print(
                f"No valid records in sheet '{sheet_name}' "
                "after initial validation."
            )
            continue

        # 4. URL Validation
        pending_url_df = valid_df[
            valid_df["processing_status"] == "PENDING"
        ].copy()

        valid_df, step2_failed_df = process_resume_urls(
            pending_url_df
        )

        if not step2_failed_df.empty:
            master_failed_dfs.append(step2_failed_df)

        if valid_df.empty:
            continue

        master_valid_dfs.append(valid_df)

    # Combine valid records across all sheets
    if not master_valid_dfs:
        print("\nNo candidate rows passed validation.")

        combined_failed_df = (
            pd.concat(master_failed_dfs, ignore_index=True)
            if master_failed_dfs
            else pd.DataFrame()
        )

        return pd.DataFrame(), combined_failed_df, []

    combined_valid_df = pd.concat(
        master_valid_dfs,
        ignore_index=True,
    )

    # 5. Cross-Team Deduplication

    # 5a. Check cross-team email duplicates
    combined_valid_df, email_failed_df = (
        check_cross_team_email_duplicates(combined_valid_df)
    )

    if not email_failed_df.empty:
        master_failed_dfs.append(email_failed_df)

    # 5b. Check duplicate resume links/files
    final_valid_df, resume_failed_df = check_duplicate_resumes(
        combined_valid_df
    )

    if not resume_failed_df.empty:
        master_failed_dfs.append(resume_failed_df)

    # Master failure consolidation
    final_failed_df = (
        pd.concat(master_failed_dfs, ignore_index=True)
        if master_failed_dfs
        else pd.DataFrame()
    )

    # 6&7. Resume Downloader $ Parser
    pipeline_results = []
    
    pending_download_df = final_valid_df[
        final_valid_df["processing_status"] == "PENDING"
    ]

    print(
        f"\nStarting resume downloads for "
        f"{len(pending_download_df)} valid candidate(s)..."
    )

    for idx, row in pending_download_df.iterrows():
        candidate_name = (
            row.get("Lead_name")
            or row.get("name")
            or f"Candidate_{idx}"
        )

        resume_url = row.get("resume_url")

        print(f"Processing candidate [{idx}]: {candidate_name}")

        # Step 6: Download resume into memory
        dl_result = download_resume_in_memory(resume_url)

        parsed_data = {}
        parsing_status = "SKIPPED"
        parsing_error = None

        # Step 7: Parse resume if download succeeded
        if dl_result.get("success") and dl_result.get("resume_text"):
            parse_res = parse_resume(dl_result["resume_text"])
            parsing_status = parse_res.get("parsing_status", "FAILED")
            parsed_data = parse_res.get("candidate_data", {})
            parsing_error = parse_res.get("error_reason")

            if parsing_status == "SUCCESS":
                print(f"  ✓ Parsed Skills: {parsed_data.get('technical_skills', [])}")
            else:
                print(f"  ✗ Parsing failed: {parsing_error}")
        else:
            print(f"  ✗ Download failed: {dl_result.get('reason')}")

        pipeline_results.append(
            {
                "candidate_index": idx,
                "candidate_name": candidate_name,
                "resume_url": resume_url,
                "download_success": dl_result.get("success", False),
                "download_reason": dl_result.get("reason"),
                "parsing_status": parsing_status,
                "parsing_error": parsing_error,
                "candidate_data": parsed_data,
                "raw_resume_text": dl_result.get("resume_text", ""),
            }
        )



    return final_valid_df, final_failed_df, pipeline_results


if __name__ == "__main__":
    # Example standalone usage
    valid_df, failed_df, downloaded_resumes = run_pipeline(
        "Original.xlsx"
    )

    successful_parses = sum(
        1
        for resume in downloaded_resumes
        if resume.get("parsing_status") == "SUCCESS"
    )

    print("\n================ PIPELINE SUMMARY ================")
    print(f"Total Valid Candidates Queued: {len(valid_df)}")
    print(f"Total Failed Candidates Logged: {len(failed_df)}")
    print(
        f"Total Resumes Processed in Memory: "
        f"{len(downloaded_resumes)}"
    )
    print(f"Total Resumes Successfully Parsed: {successful_parses}")