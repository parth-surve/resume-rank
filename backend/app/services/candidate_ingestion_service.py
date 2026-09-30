import logging
from sqlalchemy.orm import Session

from app.db.models import Candidate, Resume, Team, TeamMember

logger = logging.getLogger(__name__)

class CandidateIngestionService:
    def __init__(self, db: Session):
        self.db = db

    def ingest_candidates(self, valid_df, hackathon_id: int, domain_id: int):
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
                    mobile=row.get("phone") or row.get("mobile"),
                    college=row.get("college"),
                    linkedin_url=row.get("linkedin_url") or row.get("linkedin"),
                    github_url=row.get("github_url") or row.get("github"),
                )

                self.db.add(candidate)
                self.db.flush()

                created_candidates.append(candidate)

            # Create team
            team_name = row.get("team_name")
            if team_name:
                team = self.db.query(Team).filter(
                    Team.hackathon_id == hackathon_id,
                    Team.domain_id == domain_id,
                    Team.team_name == team_name
                ).first()
                if not team:
                    team = Team(
                        hackathon_id=hackathon_id,
                        domain_id=domain_id,
                        team_name=team_name
                    )
                    self.db.add(team)
                    self.db.flush()
                
                # Create team member
                team_member = self.db.query(TeamMember).filter(
                    TeamMember.team_id == team.id,
                    TeamMember.candidate_id == candidate.id
                ).first()
                if not team_member:
                    team_member = TeamMember(
                        team_id=team.id,
                        candidate_id=candidate.id,
                        is_team_lead=False
                    )
                    self.db.add(team_member)
                    self.db.flush()

            # Create resume for the candidate
            resume_url = row.get("resume_url")

            if resume_url:
                existing_resume = self.db.query(Resume).filter(
                    Resume.candidate_id == candidate.id,
                    Resume.resume_url == resume_url
                ).first()
                if not existing_resume:
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