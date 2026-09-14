import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


# ============================================================
# ENUMS
# ============================================================

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    ORGANIZER = "ORGANIZER"
    SUPERADMIN = "SUPERADMIN"


class ScreeningStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class CandidateProcessingStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ExtractionStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class ScreeningResultStatus(str, enum.Enum):
    PENDING = "PENDING"
    SELECTED = "SELECTED"
    WAITLISTED = "WAITLISTED"
    REJECTED = "REJECTED"


class ProcessingStage(str, enum.Enum):
    UPLOAD = "UPLOAD"
    EXTRACTION = "EXTRACTION"
    EVALUATION = "EVALUATION"
    SCORING = "SCORING"


# ============================================================
# USER
# ============================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        nullable=False,
        default=UserRole.ORGANIZER,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


# ============================================================
# HACKATHON
# ============================================================

class Hackathon(Base):
    __tablename__ = "hackathons"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    start_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    end_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


# ============================================================
# DOMAIN
# ============================================================

class Domain(Base):
    __tablename__ = "domains"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    hackathon_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("hackathons.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


# ============================================================
# IMPORT
# ============================================================

class Import(Base):
    __tablename__ = "imports"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    hackathon_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("hackathons.id"),
        nullable=False,
    )

    domain_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("domains.id"),
        nullable=False,
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


# ============================================================
# CANDIDATE
# ============================================================

class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    mobile: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    college: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    linkedin_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    github_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


# ============================================================
# TEAM
# ============================================================

class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    hackathon_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("hackathons.id"),
        nullable=False,
    )

    domain_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("domains.id"),
        nullable=False,
    )

    team_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


# ============================================================
# TEAM MEMBERS
# ============================================================

class TeamMember(Base):
    __tablename__ = "team_members"

    __table_args__ = (
        UniqueConstraint(
            "team_id",
            "candidate_id",
            name="uq_team_candidate",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    team_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("teams.id"),
        nullable=False,
    )

    candidate_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("candidates.id"),
        nullable=False,
    )

    is_team_lead: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )


# ============================================================
# RESUME
# ============================================================

class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    candidate_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("candidates.id"),
        nullable=False,
    )

    resume_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    hashed_file: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    file_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    extraction_status: Mapped[ExtractionStatus] = mapped_column(
        Enum(ExtractionStatus, name="extraction_status"),
        nullable=False,
        default=ExtractionStatus.PENDING,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


# ============================================================
# SCREENING
# ============================================================

class Screening(Base):
    __tablename__ = "screenings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    hackathon_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("hackathons.id"),
        nullable=False,
    )

    domain_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("domains.id"),
        nullable=False,
    )

    status: Mapped[ScreeningStatus] = mapped_column(
        Enum(ScreeningStatus, name="screening_status"),
        nullable=False,
        default=ScreeningStatus.PENDING,
    )

    total_candidates: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    processed_candidates: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    failed_candidates: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    selection_limit: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    waitlist_limit: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


# ============================================================
# CANDIDATE PROCESSING
# ============================================================

class CandidateProcessing(Base):
    __tablename__ = "candidate_processing"

    __table_args__ = (
        UniqueConstraint(
            "screening_id",
            "candidate_id",
            name="uq_screening_candidate",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    screening_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("screenings.id"),
        nullable=False,
    )

    candidate_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("candidates.id"),
        nullable=False,
    )

    team_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("teams.id"),
        nullable=True,
    )

    status: Mapped[CandidateProcessingStatus] = mapped_column(
        Enum(
            CandidateProcessingStatus,
            name="candidate_processing_status",
        ),
        nullable=False,
        default=CandidateProcessingStatus.PENDING,
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


# ============================================================
# PROCESSING FAILURE
# ============================================================

class ProcessingFailure(Base):
    __tablename__ = "processing_failures"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    candidate_processing_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("candidate_processing.id"),
        nullable=False,
    )

    stage: Mapped[ProcessingStage] = mapped_column(
        Enum(ProcessingStage, name="processing_stage"),
        nullable=False,
    )

    error_code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    error_message: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    failed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


# ============================================================
# PROMPT
# ============================================================

class Prompt(Base):
    __tablename__ = "prompts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    prompt_version: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    prompt_text: Mapped[str] = mapped_column(
        String(10000),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


# ============================================================
# RUBRIC
# ============================================================

class Rubric(Base):
    __tablename__ = "rubrics"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    rubric_version: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    rubric_definition: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    technical_skills_max: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=20,
    )

    competitive_achievement_max: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=15,
    )

    relevant_experience_max: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=15,
    )

    projects_max: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=25,
    )

    demonstrated_potential_max: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=15,
    )

    domain_relevance_max: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=10,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


# ============================================================
# EVALUATION
# ============================================================

class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    candidate_processing_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("candidate_processing.id"),
        nullable=False,
    )

    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    prompt_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    rubric_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Complete structured output from the AI evaluator.
    evaluation_data: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    technical_skills_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    competitive_achievement_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    relevant_experience_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    projects_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    demonstrated_potential_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    domain_relevance_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    final_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


# ============================================================
# SCREENING RESULT
# ============================================================

class ScreeningResult(Base):
    __tablename__ = "screening_results"

    __table_args__ = (
        UniqueConstraint(
            "screening_id",
            "candidate_processing_id",
            name="uq_screening_processing",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    screening_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("screenings.id"),
        nullable=False,
    )

    candidate_processing_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("candidate_processing.id"),
        nullable=False,
    )

    evaluation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("evaluations.id"),
        nullable=False,
    )

    final_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    result_status: Mapped[ScreeningResultStatus] = mapped_column(
        Enum(
            ScreeningResultStatus,
            name="screening_result_status",
        ),
        nullable=False,
        default=ScreeningResultStatus.PENDING,
    )

    rank: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


# ============================================================
# MANUAL OVERRIDE
# ============================================================

class ManualOverride(Base):
    __tablename__ = "manual_overrides"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    screening_result_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("screening_results.id"),
        nullable=False,
        index=True,
    )

    previous_status: Mapped[ScreeningResultStatus] = mapped_column(
        Enum(
            ScreeningResultStatus,
            name="screening_result_status",
        ),
        nullable=False,
    )

    new_status: Mapped[ScreeningResultStatus] = mapped_column(
        Enum(
            ScreeningResultStatus,
            name="screening_result_status",
        ),
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    overridden_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )