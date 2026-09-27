"""Download and extract public PDF resumes with bounded resource use."""

import io
from urllib.parse import urljoin

import pymupdf
import requests

from data_pipeline.url_validator import validate_and_convert_url


MAX_RESUME_DOWNLOAD_BYTES = 15 * 1024 * 1024
MAX_REDIRECTS = 5


def download_resume_in_memory(url: str, timeout: int = 15) -> dict:
    """Fetch a validated public URL without following unchecked redirects."""
    current_url = url
    content = bytearray()

    try:
        for redirect_count in range(MAX_REDIRECTS + 1):
            validation = validate_and_convert_url(current_url)
            if not validation["is_valid"]:
                return {
                    "success": False,
                    "resume_text": "",
                    "reason": validation["reason"],
                }
            current_url = validation["download_url"]

            with requests.get(
                current_url,
                timeout=timeout,
                stream=True,
                allow_redirects=False,
            ) as response:
                if response.is_redirect or response.is_permanent_redirect:
                    location = response.headers.get("Location")
                    if not location or redirect_count == MAX_REDIRECTS:
                        return {
                            "success": False,
                            "resume_text": "",
                            "reason": "Too many or invalid redirects",
                        }
                    current_url = urljoin(current_url, location)
                    continue

                if response.status_code != 200:
                    return {"success": False, "resume_text": "", "reason": f"HTTP status {response.status_code}"}

                declared_length = response.headers.get("Content-Length")
                if declared_length and int(declared_length) > MAX_RESUME_DOWNLOAD_BYTES:
                    return {
                        "success": False,
                        "resume_text": "",
                        "reason": "Resume file exceeds the maximum allowed size",
                    }

                for chunk in response.iter_content(chunk_size=64 * 1024):
                    if not chunk:
                        continue
                    content.extend(chunk)
                    if len(content) > MAX_RESUME_DOWNLOAD_BYTES:
                        return {
                            "success": False,
                            "resume_text": "",
                            "reason": "Resume file exceeds the maximum allowed size",
                        }
                break
        else:
            return {"success": False, "resume_text": "", "reason": "Too many redirects"}

        with pymupdf.open(stream=io.BytesIO(content), filetype="pdf") as doc:
            if doc.is_encrypted:
                return {"success": False, "resume_text": "", "reason": "Encrypted PDF file"}
            text = "\n".join(
                page.get_text("text") for page in doc
                if page.get_text("text").strip()
            ).strip()
        if not text:
            return {"success": False, "resume_text": "", "reason": "Scanned image or empty PDF"}
        return {"success": True, "resume_text": text, "reason": None}
    except requests.exceptions.Timeout:
        return {"success": False, "resume_text": "", "reason": "Connection timeout"}
    except requests.exceptions.RequestException as exc:
        return {
            "success": False,
            "resume_text": "",
            "reason": f"Network failure: {type(exc).__name__}",
        }
    except Exception:
        # Keep URLs, resume content, and parser diagnostics out of logs/results.
        return {"success": False, "resume_text": "", "reason": "Processing error"}
