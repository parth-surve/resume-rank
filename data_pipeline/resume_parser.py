import re
import logging
from typing import Dict, Any, List, Optional
from resume_downloader import download_resume_in_memory

# Set up logger for parser debugging
logger = logging.getLogger(__name__)

# Default skill taxonomy for candidate matching
DEFAULT_SKILL_TAXONOMY = [
    "python", "pandas", "numpy", "matplotlib", "scikit-learn", "tensorflow", "pytorch",
    "c++", "c", "java", "javascript", "typescript", "html", "css", "react", "node.js",
    "sql", "postgresql", "mysql", "mongodb", "git", "github", "docker", "aws",
    "data structures", "algorithms", "rest api", "fastapi", "flask", "django"
]


def clean_resume_text(text: Any) -> str:
    """
    Sanitizes raw extracted text from PDF.
    Safely handles non-string inputs and regex errors.
    """
    if not text or not isinstance(text, str):
        return ""
    
    try:
        # remove control characters but preserve Unicode letters
        cleaned=text.replace('\xa0','')
        cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]','',cleaned)
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)
        cleaned = re.sub(r'\n+', '\n', cleaned)
        return cleaned.strip()
    except Exception as e:
        logger.warning(f"Error during text sanitization: {e}")
        return str(text).strip() if text else ""


def extract_email(text: str) -> Optional[str]:
    """Safely extracts candidate email address."""
    if not text:
        return None
    try:
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        return match.group(0).lower() if match else None
    except Exception as e:
        logger.warning(f"Failed email extraction: {e}")
        return None


def extract_phone(text: str) -> Optional[str]:
    """Safely extracts phone numbers."""
    if not text:
        return None
    try:
        phone_pattern = (r"(?<!\w)"
        r"(?:\+91[\s.-]?|91[\s.-]?)?"
        r"[6-9]\d{4}[\s.-]?\d{5}"
        r"(?!\w)")
        match = re.search(phone_pattern, text)
        if match:
            phone = match.group(0).strip()
            # Validate numeric length to avoid capturing years or short numbers
            if len(re.sub(r'\D', '', phone)) >= 10:
                return phone
        return None
    except Exception as e:
        logger.warning(f"Failed phone extraction: {e}")
        return None


def extract_linkedin(text: str) -> Optional[str]:
    """Safely extracts LinkedIn profile URL."""
    if not text:
        return None
    try:
        linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?'
        match = re.search(linkedin_pattern, text, re.IGNORECASE)
        if match:
            url= match.group(0).strip() if match else None
            if not url.lower().startswith("http"):
                url = "https://"+url
            return url
    except Exception as e:
        logger.warning(f"Failed LinkedIn extraction: {e}")
        return None


def extract_name(text: str) -> Optional[str]:
    """
    Safely extracts candidate name from header lines.
    """
    if not text:
        return None
    try:
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for line in lines[:3]:
            # Skip noise lines containing emails, phones, or 'resume' keywords
            if (
                extract_email(line) 
                or extract_phone(line) 
                or "resume" in line.lower() 
                or "curriculum" in line.lower()
                or "cv" in line.lower()
            ):
                continue
            
            words = line.split()
            if 1 <= len(words) <= 4 and not any(char.isdigit() for char in line):
                clean_name = re.sub(r'[^a-zA-Z\s]', '', line).strip()
                if clean_name:
                    return clean_name.title()
        return None
    except Exception as e:
        logger.warning(f"Failed name extraction: {e}")
        return None


def extract_sections(text: str) -> Dict[str, str]:
    """
    Segments resume into key section blocks (Education, Experience, Projects, Skills, Achievements).
    Catches slicing and regex bounds errors gracefully.
    """
    default_sections = {
        "education": "",
        "experience": "",
        "projects": "",
        "technical_skills": "",
        "achievements": ""
    }
    
    if not text:
        return default_sections

    try:
        headers = {
            "education": r'(?i)\b(education|academic background|qualifications)\b',
            "experience": r'(?i)\b(work experience|experience|employment history|internships)\b',
            "projects": r'(?i)\b(projects|key projects|academic projects)\b',
            "technical_skills": r'(?i)\b(technical skills|skills|tech stack|key competencies)\b',
            "achievements": r'(?i)\b(achievements|accomplishments|awards|certifications|honors)\b'
        }

        found_sections = []
        for section_name, pattern in headers.items():
            for match in re.finditer(pattern, text):
                found_sections.append((match.start(), section_name))

        found_sections.sort()
        sections_content = default_sections.copy()

        for i in range(len(found_sections)):
            start_idx = found_sections[i][0]
            section_key = found_sections[i][1]
            end_idx = found_sections[i + 1][0] if i + 1 < len(found_sections) else len(text)
            
            section_text = text[start_idx:end_idx].strip()
            lines = section_text.split('\n')
            
            # Omit the header title line itself
            sections_content[section_key] = "\n".join(lines[1:]).strip() if len(lines) > 1 else section_text

        return sections_content

    except Exception as e:
        logger.error(f"Error while parsing resume sections: {e}")
        return default_sections


def extract_skills(text: str, taxonomy: Optional[List[str]] = None) -> List[str]:
    """Safely matches text against skill taxonomy."""
    if not text:
        return []
    
    skill_list = taxonomy if taxonomy is not None else DEFAULT_SKILL_TAXONOMY
    detected_skills = []
    
    try:
        for skill in skill_list:
            if skill.lower() in ("c++", "c#"):
             pattern = (
                r"(?<![A-Za-z0-9])"
                + re.escape(skill)
                + r"(?![A-Za-z0-9])"
              )
        else:
            pattern = (
                r"(?<!\w)"
                + re.escape(skill)
                + r"(?!\w)"
            )

        if re.search(pattern, text, re.IGNORECASE):
            detected_skills.append(skill)

        return sorted(set(detected_skills), key=str.lower)
    except Exception as e:
        logger.warning(f"Error during skill matching: {e}")
        return []


def parse_resume(raw_resume_text: Any) -> Dict[str, Any]:
    """
    Main execution wrapper for resume parsing.
    Guarantees a clean dictionary return even if internal errors occur.
    """
    try:
        # Step 1: Input Validation & Sanitization
        if not raw_resume_text or not isinstance(raw_resume_text, str):
            return {
                "parsing_status": "FAILED",
                "error_reason": "Invalid or non-string raw text input",
                "candidate_data": {},
                "cleaned_text": ""
            }

        cleaned_text = clean_resume_text(raw_resume_text)
        
        if not cleaned_text:
            return {
                "parsing_status": "FAILED",
                "error_reason": "Text empty after sanitization",
                "candidate_data": {},
                "cleaned_text": ""
            }

        # Step 2: Extract Sections & Details
        sections = extract_sections(cleaned_text)
        skills_source = sections["technical_skills"] if sections["technical_skills"] else cleaned_text
        
        candidate_data = {
            "name": extract_name(cleaned_text),
            "email": extract_email(cleaned_text),
            "contact": extract_phone(cleaned_text),
            "linkedin": extract_linkedin(cleaned_text),
            "technical_skills": extract_skills(skills_source),
            "education": sections.get("education", ""),
            "experience": sections.get("experience", ""),
            "projects": sections.get("projects", ""),
            "achievements": sections.get("achievements", "")
        }

        return {
            "parsing_status": "SUCCESS",
            "error_reason": None,
            "candidate_data": candidate_data,
            "cleaned_text": cleaned_text
        }

    except Exception as fatal_error:
        # Fallback catch-all to prevent entire pipeline runner crash
        logger.error(f"Fatal crash inside parse_resume: {fatal_error}", exc_info=True)
        return {
            "parsing_status": "FAILED",
            "error_reason": f"Unhandled parser error: {str(fatal_error)}",
            "candidate_data": {},
            "cleaned_text": ""
        }