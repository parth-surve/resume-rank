import logging
from sqlalchemy.orm import Session

from app.db.models import Candidate, Resume

logger = logging.getLogger(__name__)

class CandidateIngestionService:
    def __init__(self, db: Session):
        self.db = db

    def ingest_candidates(self, valid_df):
        created_candidates = []
        created_resumes = []

        for _, row in valid_df.iterrows():
            email = row.get("email")

            # Check whether candidate already exists
            candidate = (
                self.db.query(Candidate)
                .filter(Candidate.email == email)
                .first()
            )

            # Create candidate if they don't already exist
            if not candidate:
                candidate = Candidate(
                    name=row.get("name"),
                    email=email,
                    mobile=row.get("phone"),
                    college=row.get("college"),
                    linkedin_url=row.get("linkedin"),
                    github_url=row.get("github"),
                )

                self.db.add(candidate  )
                self.db.flush()

                created_candidates.append(candidate)

            # Create resume for the candidate
            resume_url = row.get("resume_url")

            if resume_url:
                resume = Resume(
                    candidate_id=candidate.id,
                    resume_url=resume_url,
                    file_type="pdf",
                    file_size=0,
                )

                self.db.add(resume)
                created_resumes.append(resume)

        self.db.commit()

        logger.info(
            "Candidate ingestion completed: candidates_created=%s resumes_created=%s",
            len(created_candidates),
            len(created_resumes),
        )

        return created_candidates, created_resumes