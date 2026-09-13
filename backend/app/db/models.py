# from datetime import datetime
# from sqlalchemy import String, DateTime, func, Integer,UniqueConstraint,Float
# from sqlalchemy.orm import Mapped, mapped_column
# import enum
# from sqlalchemy import Enum as SQLEnum

# from app.db.database import Base


# class Hackathon(Base):
#     __tablename__ = "hackathons"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(255))
#     description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
#     created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
# from sqlalchemy import ForeignKey

# class Domain(Base):
#     __tablename__ = "domains"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     name: Mapped[str] = mapped_column(String(255))
#     hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons.id"))
#     created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    
# class Import(Base):
#     __tablename__ = "imports"
#     id:Mapped[int] = map
#     id: Mapped[int] = mapped_column(primary_key=True)
#     hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons.id"))
#     domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id"))
#     filename: Mapped[str] = mapped_column(String(255))
#     file_path: Mapped[str] = mapped_column(String(500))
#     created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    
# class ScreeningStatus(str, enum.Enum):
#     PENDING = "PENDING"
#     PROCESSING = "PROCESSING"
#     COMPLETED = "COMPLETED"
#     FAILED = "FAILED"
    
# class ProcessingStatus(str, enum.Enum):
#     PENDING = "PENDING"
#     PROCESSING = "PROCESSING"
#     COMPLETED = "COMPLETED"
#     FAILED = "FAILED"


# class FinalDecision(str, enum.Enum):
#     SELECTED = "SELECTED"
#     WAITLIST = "WAITLIST"
#     REJECTED = "REJECTED"
    
# class Screening(Base):
#     __tablename__ = "screenings"
    
#     id: Mapped[int] = mapped_column(primary_key=True)
#     hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons_id"))
#     domain_id: Mapped[int] = mapped_column(ForeignKey("domains_id"))
    
#     selection_limit: Mapped[int] = mapped_column(Integer)
#     waitlist_limit: Mapped[int] = mapped_column(Integer)
#     rubric_version: Mapped[str] = mapped_column(String(50))

#     status: Mapped[ScreeningStatus] = mapped_column(SQLEnum(ScreeningStatus), default=ScreeningStatus.PENDING)
    
#     total: Mapped[int] = mapped_column(Integer, default=0)
#     processed: Mapped[int] = mapped_column(Integer, default=0)
#     successful: Mapped[int] = mapped_column(Integer, default=0)
#     failed: Mapped[int] = mapped_column(Integer, default=0)

#     created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    
# class Candidate(Base):
#     __tablename__ = "candidates"
#     __table_args__ = (
#         UniqueConstraint("hackathon_id", "domain_id", "email", name="uq_candidate_per_domain"),
#     )

#     id: Mapped[int] = mapped_column(primary_key=True)
#     hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons.id"))
#     domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id"))

#     name: Mapped[str] = mapped_column(String(255))
#     email: Mapped[str] = mapped_column(String(255))
#     college: Mapped[str | None] = mapped_column(String(255), nullable=True)
#     resume_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
#     github: Mapped[str | None] = mapped_column(String(255), nullable=True)
#     linkedin: Mapped[str | None] = mapped_column(String(255), nullable=True)

#     processing_status: Mapped[ProcessingStatus] = mapped_column(
#         SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING
#     )
#     final_decision: Mapped[FinalDecision | None] = mapped_column(SQLEnum(FinalDecision), nullable=True)
#     final_score: Mapped[float | None] = mapped_column(Float, nullable=True)
#     rank: Mapped[int | None] = mapped_column(Integer, nullable=True)

#     failure_stage: Mapped[str | None] = mapped_column(String(100), nullable=True)
#     failure_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
#     failure_reason: Mapped[str | None] = mapped_column(String(1000), nullable=True)
#     retry_count: Mapped[int] = mapped_column(Integer, default=0)

#     created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


from datetime import datetime
from sqlalchemy import (
    String, DateTime, func, Integer, UniqueConstraint, Float, ForeignKey, JSON
)
from sqlalchemy.orm import Mapped, mapped_column
import enum
from sqlalchemy import Enum as SQLEnum

from app.db.database import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ScreeningStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"          # added from teammate's ScreeningStatus


class ProcessingStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class FinalDecision(str, enum.Enum):
    SELECTED = "SELECTED"
    WAITLIST = "WAITLIST"
    REJECTED = "REJECTED"


class UserRole(str, enum.Enum):        # added from teammate's file
    ADMIN = "ADMIN"
    ORGANIZER = "ORGANIZER"
    SUPERADMIN = "SUPERADMIN"


class ExtractionStatus(str, enum.Enum):    # added
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class ProcessingStage(str, enum.Enum):     # added — used by ProcessingFailure
    UPLOAD = "UPLOAD"
    EXTRACTION = "EXTRACTION"
    EVALUATION = "EVALUATION"
    SCORING = "SCORING"


# ---------------------------------------------------------------------------
# Core tables (your originals — bugs fixed, names unchanged)
# ---------------------------------------------------------------------------

class Hackathon(Base):
    __tablename__ = "hackathons"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Domain(Base):
    __tablename__ = "domains"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Import(Base):
    __tablename__ = "imports"

    id: Mapped[int] = mapped_column(primary_key=True)     # fixed: removed the broken duplicate line
    hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons.id"))
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id"))
    filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Screening(Base):
    __tablename__ = "screenings"

    id: Mapped[int] = mapped_column(primary_key=True)
    hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons.id"))    # fixed: was "hackathons_id"
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id"))           # fixed: was "domains_id"

    selection_limit: Mapped[int] = mapped_column(Integer)
    waitlist_limit: Mapped[int] = mapped_column(Integer)
    rubric_version: Mapped[str] = mapped_column(String(50))

    status: Mapped[ScreeningStatus] = mapped_column(SQLEnum(ScreeningStatus), default=ScreeningStatus.PENDING)

    total: Mapped[int] = mapped_column(Integer, default=0)
    processed: Mapped[int] = mapped_column(Integer, default=0)
    successful: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)

    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)     # added from teammate
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)   # added from teammate

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Candidate(Base):
    """
    Equivalent to teammate's CandidateMaster, merged with her `mobile`
    field, keeping your name/table/uniqueness design (per hackathon+domain,
    not globally unique — a person can legitimately apply to two different
    hackathons or domains).
    """
    __tablename__ = "candidates"
    __table_args__ = (
        UniqueConstraint("hackathon_id", "domain_id", "email", name="uq_candidate_per_domain"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons.id"))
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id"))

    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    mobile: Mapped[str | None] = mapped_column(String(15), nullable=True)   # added from teammate
    college: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resume_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    github: Mapped[str | None] = mapped_column(String(255), nullable=True)
    linkedin: Mapped[str | None] = mapped_column(String(255), nullable=True)

    processing_status: Mapped[ProcessingStatus] = mapped_column(
        SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING
    )
    final_decision: Mapped[FinalDecision | None] = mapped_column(SQLEnum(FinalDecision), nullable=True)
    final_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)

    failure_stage: Mapped[str | None] = mapped_column(String(100), nullable=True)
    failure_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


# ---------------------------------------------------------------------------
# Added in full from teammate's schema (converted UUID -> int for consistency)
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.ORGANIZER)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class HackathonDomain(Base):
    """
    NOTE: potential overlap with Domain.hackathon_id above. Domain already
    ties one domain to one hackathon directly. This join table would only
    be needed if a domain should be reusable across multiple hackathons
    (many-to-many). Kept here per teammate's design, but not currently
    used by any service/route — confirm with the team which relationship
    model is the real one before wiring anything to this table.
    """
    __tablename__ = "hackathon_domain"
    __table_args__ = (UniqueConstraint("hackathon_id", "domain_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons.id"))
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id"))


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons.id"))
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id"))
    team_name: Mapped[str] = mapped_column(String(255), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class TeamMember(Base):
    __tablename__ = "team_members"
    __table_args__ = (UniqueConstraint("team_id", "candidate_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"))
    is_team_lead: Mapped[str] = mapped_column(SQLEnum("yes", "no", name="team_lead_status"), default="no")


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"))
    resume_url: Mapped[str] = mapped_column(String(500))
    hashed_file: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_type: Mapped[str] = mapped_column(String(50))
    file_size: Mapped[int] = mapped_column(Integer)
    extraction_status: Mapped[ExtractionStatus] = mapped_column(
        SQLEnum(ExtractionStatus), default=ExtractionStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class CandidateProcessing(Base):
    """
    Tracks a candidate's processing attempt PER screening — distinct from
    Candidate.processing_status, which only tracks the most recent/single
    attempt. This matters once a candidate can be part of more than one
    screening over time (e.g. reused across two different hackathons).
    """
    __tablename__ = "candidate_processing"
    __table_args__ = (UniqueConstraint("screening_id", "candidate_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    screening_id: Mapped[int] = mapped_column(ForeignKey("screenings.id"))
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"))
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True)

    status: Mapped[ProcessingStatus] = mapped_column(SQLEnum(ProcessingStatus), default=ProcessingStatus.PENDING)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ProcessingFailure(Base):
    __tablename__ = "processing_failures"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_processing_id: Mapped[int] = mapped_column(ForeignKey("candidate_processing.id"))
    stage: Mapped[ProcessingStage] = mapped_column(SQLEnum(ProcessingStage))
    error_code: Mapped[str] = mapped_column(String(100))
    error_message: Mapped[str] = mapped_column(String(1000))
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Prompt(Base):
    __tablename__ = "prompts"

    id: Mapped[int] = mapped_column(primary_key=True)
    prompt_version: Mapped[str] = mapped_column(String(50), unique=True)
    prompt_text: Mapped[str] = mapped_column(String(5000))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Rubric(Base):
    __tablename__ = "rubrics"

    id: Mapped[int] = mapped_column(primary_key=True)
    rubric_version: Mapped[str] = mapped_column(String(50), unique=True)
    rubric_definition: Mapped[dict] = mapped_column(JSON)

    technical_skills_max: Mapped[int] = mapped_column(Integer, default=20)
    competitive_achievement_max: Mapped[int] = mapped_column(Integer, default=15)
    relevant_experience_max: Mapped[int] = mapped_column(Integer, default=15)
    projects_max: Mapped[int] = mapped_column(Integer, default=25)
    demonstrated_potential_max: Mapped[int] = mapped_column(Integer, default=15)
    domain_relevance_max: Mapped[int] = mapped_column(Integer, default=10)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Evaluation(Base):
    """
    Uses the 6-category rubric from the teammate's schema. Now tied to
    CandidateProcessing (per-screening attempt) rather than directly to
    Candidate, matching her design — this is more correct once a candidate
    can be evaluated across multiple screenings.
    """
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_processing_id: Mapped[int] = mapped_column(ForeignKey("candidate_processing.id"))

    model: Mapped[str] = mapped_column(String(100))
    prompt_version: Mapped[str] = mapped_column(String(50))
    rubric_version: Mapped[str] = mapped_column(String(50))

    technical_skills_score: Mapped[int] = mapped_column(Integer)
    technical_skills_evidence: Mapped[list[str]] = mapped_column(JSON)
    technical_skills_reason: Mapped[str] = mapped_column(String(2000))

    competitive_achievement_score: Mapped[int] = mapped_column(Integer)
    competitive_achievement_evidence: Mapped[list[str]] = mapped_column(JSON)
    competitive_achievement_reason: Mapped[str] = mapped_column(String(2000))

    relevant_experience_score: Mapped[int] = mapped_column(Integer)
    relevant_experience_evidence: Mapped[list[str]] = mapped_column(JSON)
    relevant_experience_reason: Mapped[str] = mapped_column(String(2000))

    projects_score: Mapped[int] = mapped_column(Integer)
    projects_evidence: Mapped[list[str]] = mapped_column(JSON)
    projects_reason: Mapped[str] = mapped_column(String(2000))

    demonstrated_potential_score: Mapped[int] = mapped_column(Integer)
    demonstrated_potential_evidence: Mapped[list[str]] = mapped_column(JSON)
    demonstrated_potential_reason: Mapped[str] = mapped_column(String(2000))

    domain_relevance_score: Mapped[int] = mapped_column(Integer)
    domain_relevance_evidence: Mapped[list[str]] = mapped_column(JSON)
    domain_relevance_reason: Mapped[str] = mapped_column(String(2000))

    final_score: Mapped[int] = mapped_column(Integer)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ScreeningResult(Base):
    __tablename__ = "screening_results"
    __table_args__ = (UniqueConstraint("screening_id", "candidate_processing_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    screening_id: Mapped[int] = mapped_column(ForeignKey("screenings.id"))
    candidate_processing_id: Mapped[int] = mapped_column(ForeignKey("candidate_processing.id"))
    evaluation_id: Mapped[int] = mapped_column(ForeignKey("evaluations.id"))

    final_score: Mapped[int] = mapped_column(Integer)
    result_status: Mapped[FinalDecision | None] = mapped_column(SQLEnum(FinalDecision), nullable=True)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class DecisionOverride(Base):
    """
    Equivalent to teammate's ManualOverride — kept your name, linked to
    ScreeningResult (matching her more granular design) instead of
    directly to Candidate.
    """
    __tablename__ = "decision_overrides"

    id: Mapped[int] = mapped_column(primary_key=True)
    screening_result_id: Mapped[int] = mapped_column(ForeignKey("screening_results.id"), index=True)
    original_decision: Mapped[str | None] = mapped_column(String(50), nullable=True)
    new_decision: Mapped[str] = mapped_column(String(50))
    reason: Mapped[str] = mapped_column(String(1000))
    changed_by: Mapped[str] = mapped_column(String(255))   # will become a User FK once auth is built
    changed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())