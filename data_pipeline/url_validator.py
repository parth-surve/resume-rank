from typing import Dict, Any, Tuple
import socket
import ipaddress
import re
from urllib.parse import urlparse
import pandas as pd

ALLOWED_SCHEMES = {"http", "https"}

def is_public_ip(hostname: str) -> bool:
    """Resolve every address and reject hosts with any non-public result."""
    try:
        addresses = {
            result[4][0]
            for result in socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
        }
        return bool(addresses) and all(
            ipaddress.ip_address(address).is_global for address in addresses
        )
    except Exception:
        return False


def validate_and_convert_url(url: str) -> dict:
    """Pure utility: Validates a single URL string and converts Google Drive links."""
    if not isinstance(url, str) or not url.strip():
        return {"is_valid": False, "reason": "URL is empty", "download_url": None}

    clean_url = url.strip()

    try:
        parsed = urlparse(clean_url)

        if parsed.scheme not in ALLOWED_SCHEMES:
            return {
                "is_valid": False,
                "reason": f"Unsupported scheme: {parsed.scheme}",
                "download_url": None,
            }

        if parsed.username is not None or parsed.password is not None:
            return {
                "is_valid": False,
                "reason": "Credentials in URLs are not allowed",
                "download_url": None,
            }

        try:
            parsed.port
        except ValueError:
            return {
                "is_valid": False,
                "reason": "Malformed URL port",
                "download_url": None,
            }

        if not parsed.hostname or not is_public_ip(parsed.hostname):
            return {
                "is_valid": False,
                "reason": "Restricted or invalid IP/hostname detected (SSRF protection)",
                "download_url": None,
            }

        # Google Drive transformation
        if parsed.hostname.lower() == "drive.google.com":
            drive_id_match = re.search(r"(?:/file/d/|id=)([\w-]+)", clean_url)
            if drive_id_match:
                file_id = drive_id_match.group(1)
                clean_url = f"https://drive.google.com/uc?export=download&id={file_id}"
                return {"is_valid": True, "reason": None, "download_url": clean_url}
            else:
                return {
                    "is_valid": False,
                    "reason": "Invalid Google Drive link format (missing file ID)",
                    "download_url": None,
                }

        return {"is_valid": True, "reason": None, "download_url": clean_url}

    except Exception as err:
        return {
            "is_valid": False,
            "reason": f"Malformed URL format: {str(err)}",
            "download_url": None,
        }


def process_resume_urls(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Applies URL validation across a DataFrame:
    - Sets resume_url to direct download URL
    - Valid URLs   -> processing_status = 'PENDING', failure_reason = ""
    - Invalid URLs -> processing_status = 'FAILED', failure_reason = <reason>
    """
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame(), pd.DataFrame()

    df_work = df
    valid_records = []
    failed_records = []

    for _, row in df_work.iterrows():
        row_dict = row.to_dict()
        raw_url = row_dict.get("resume_url", "")

        res = validate_and_convert_url(str(raw_url) if raw_url else "")

        if res["is_valid"]:
            row_dict["resume_url"] = res["download_url"]
            row_dict["processing_status"] = "PENDING"
            row_dict["failure_reason"] = None
            valid_records.append(row_dict)
        else:
            row_dict["processing_status"] = "FAILED"
            row_dict["failure_reason"] = res["reason"]
            failed_records.append(row_dict)

    valid_df = pd.DataFrame(valid_records) if valid_records else pd.DataFrame(columns=df_work.columns)
    failed_df = pd.DataFrame(failed_records) if failed_records else pd.DataFrame(columns=df_work.columns)

    return valid_df, failed_df
