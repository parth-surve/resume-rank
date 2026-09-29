"""Export screening results and candidate rankings into formatted Excel spreadsheets."""

import io
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import pandas as pd


def export_screening_to_excel(
    screening_metadata: Dict[str, Any],
    results_data: List[Dict[str, Any]],
) -> bytes:
    """
    Generate an in-memory Excel workbook (.xlsx) containing:
    1. 'Results': Ranked candidates with scores, subscores, decisions, contact info.
    2. 'Summary': High-level metadata of the screening run and counts.

    Returns raw bytes of the Excel file.
    """
    output = io.BytesIO()

    # Prepare DataFrame for Results
    results_rows = []
    for item in results_data:
        results_rows.append({
            "Rank": item.get("rank"),
            "Decision": item.get("decision", "PENDING"),
            "Final Score": item.get("final_score"),
            "Technical Skills (/20)": item.get("technical_skills_score"),
            "Competitive Achievement (/15)": item.get("competitive_achievement_score"),
            "Relevant Experience (/15)": item.get("relevant_experience_score"),
            "Projects (/25)": item.get("projects_score"),
            "Demonstrated Potential (/15)": item.get("demonstrated_potential_score"),
            "Domain Relevance (/10)": item.get("domain_relevance_score"),
            "Candidate Name": item.get("name", ""),
            "Email": item.get("email", ""),
            "College": item.get("college", ""),
            "Mobile": item.get("mobile", ""),
            "Domain": item.get("domain_name", ""),
            "LinkedIn": item.get("linkedin_url", ""),
            "GitHub": item.get("github_url", ""),
            "Resume URL": item.get("resume_url", ""),
            "Processing Status": item.get("processing_status", ""),
            "Failure Stage": item.get("failure_stage", ""),
            "Failure Reason": item.get("failure_reason", ""),
        })

    df_results = pd.DataFrame(results_rows) if results_rows else pd.DataFrame(columns=[
        "Rank", "Decision", "Final Score", "Technical Skills (/20)",
        "Competitive Achievement (/15)", "Relevant Experience (/15)",
        "Projects (/25)", "Demonstrated Potential (/15)",
        "Domain Relevance (/10)", "Candidate Name", "Email", "College",
        "Mobile", "Domain", "LinkedIn", "GitHub", "Resume URL",
        "Processing Status", "Failure Stage", "Failure Reason"
    ])

    # Summary metadata DataFrame
    summary_rows = [
        {"Metric": "Screening ID", "Value": screening_metadata.get("screening_id", "")},
        {"Metric": "Hackathon", "Value": screening_metadata.get("hackathon_name", "")},
        {"Metric": "Domain", "Value": screening_metadata.get("domain_name", "")},
        {"Metric": "Status", "Value": screening_metadata.get("status", "")},
        {"Metric": "Selection Limit", "Value": screening_metadata.get("selection_limit", 0)},
        {"Metric": "Waitlist Limit", "Value": screening_metadata.get("waitlist_limit", 0)},
        {"Metric": "Total Candidates", "Value": screening_metadata.get("total_candidates", 0)},
        {"Metric": "Processed Candidates", "Value": screening_metadata.get("processed_candidates", 0)},
        {"Metric": "Failed Candidates", "Value": screening_metadata.get("failed_candidates", 0)},
        {"Metric": "Selected Candidates", "Value": screening_metadata.get("selected_candidates", 0)},
        {"Metric": "Waitlisted Candidates", "Value": screening_metadata.get("waitlisted_candidates", 0)},
        {"Metric": "Rejected Candidates", "Value": screening_metadata.get("rejected_candidates", 0)},
        {"Metric": "Started At", "Value": str(screening_metadata.get("started_at", ""))},
        {"Metric": "Completed At", "Value": str(screening_metadata.get("completed_at", ""))},
        {"Metric": "Exported At", "Value": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")},
    ]
    df_summary = pd.DataFrame(summary_rows)

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_results.to_excel(writer, sheet_name="Screening Results", index=False)
        df_summary.to_excel(writer, sheet_name="Summary", index=False)

    return output.getvalue()
