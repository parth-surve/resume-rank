import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import Integer, String, DateTime, Enum, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base


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

class EvaluationCategory(str, enum.Enum):
    TECHNICAL_SKILLS = "TECHNICAL_SKILLS"
    COMPETITIVE_ACHIEVEMENT = "COMPETITIVE_ACHIEVEMENT"
    RELEVANT_EXPERIENCE = "RELEVANT_EXPERIENCE"
    PROJECTS = "PROJECTS"
    DEMONSTRATED_POTENTIAL = "DEMONSTRATED_POTENTIAL"
    DOMAIN_RELEVANCE = "DOMAIN_RELEVANCE"

class ProcessingStage(str, enum.Enum):
    UPLOAD = "UPLOAD"
    EXTRACTION = "EXTRACTION"
    EVALUATION = "EVALUATION"
    SCORING = "SCORING"    

# MASTER TABLES

class User(Base): 
    __tablename__ = "user_master"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255), 
        unique=True,
        nullable=False,
        index=True
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        nullable=False,
        default=UserRole.ORGANIZER
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
    )  
    
class Hackathon(Base):
    __tablename__ = "hackathon_master"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(
        String(255),
        unique=True, 
        nullable=False, 
        index=True
    )

    description: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
    )

    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    end_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
        
class Domain(Base):
    __tablename__ = "domain_master"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,  
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
class HackathonDomain(Base):
    __tablename__ = "hackathon_domain"
    __table_args__ = (
    UniqueConstraint("hackathon_id", "domain_id"),
)
    
    id: Mapped[uuid.UUID] = mapped_column(
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4
        )
    
    hackathon_id: Mapped[uuid.UUID] = mapped_column(
            UUID(as_uuid=True),
            ForeignKey("hackathon_master.id"),
            nullable=False
        )
    
    domain_id: Mapped[uuid.UUID] = mapped_column(
                UUID(as_uuid=True),
                ForeignKey("domain_master.id"),
                nullable=False
            )
    
class CandidateMaster(Base):

    __tablename__ = "candidate_master"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    mobile: Mapped[str] = mapped_column(
        String(15),
        unique=True,
        nullable=False
    )

    college: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    linkedin_url: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=True
    )

    github_url: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

class Team(Base):

    __tablename__ = "team"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    hackathon_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hackathon_master.id"),
        nullable=False
    )

    domain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("domain_master.id"),
        nullable=False
    )

    team_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
class TeamMember(Base):

    __tablename__ = "team_members"
    __table_args__ = (
    UniqueConstraint("team_id", "candidate_id"),
)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("team.id"),
        nullable=False
    )

    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("candidate_master.id"),
        nullable=False
    )

    is_team_lead: Mapped[str] = mapped_column(
        Enum("yes", "no", name="team_lead_status"),
        nullable=False,
        default="no"
    )

class Resume(Base):

    __tablename__ = "resume"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("candidate_master.id"),
        nullable=False
    )

    resume_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    hashed_file: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    file_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    extraction_status: Mapped[ExtractionStatus] = mapped_column(
    Enum(ExtractionStatus, name="extraction_status"),
    nullable=False,
    default=ExtractionStatus.PENDING
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
class Screening(Base):

    __tablename__ = "screening"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    hackathon_master_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hackathon_master.id"),
        nullable=False
    )

    domain_master_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("domain_master.id"),
        nullable=False
    )

    status: Mapped[ScreeningStatus] = mapped_column(
    Enum(ScreeningStatus, name="screening_status"),
    nullable=False,
    default=ScreeningStatus.PENDING
    )

    total_candidate: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    processed_candidate: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    failed_candidates: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    selection_limit: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    waitlist_limit: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

class CandidateProcessing(Base): 

    __tablename__ = "candidate_processing"
    
    __table_args__ = (
    UniqueConstraint("screening_id", "candidate_master_id"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    screening_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("screening.id"),
        nullable=False
    )

    candidate_master_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("candidate_master.id"),
        nullable=False
    )

    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("team.id"),
        nullable=True
    )

    status: Mapped[CandidateProcessingStatus] = mapped_column(
    Enum(CandidateProcessingStatus, name="candidate_processing_status"),
    nullable=False,
    default=CandidateProcessingStatus.PENDING
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

class ProcessingFailure(Base):

    __tablename__ = "processing_failures"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    candidate_processing_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("candidate_processing.id"),
        nullable=False
    )

    stage: Mapped[ProcessingStage] = mapped_column(
    Enum(ProcessingStage, name="processing_stage"),
    nullable=False
    )

    error_code: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    error_message: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    failed_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    nullable=False,
    default=lambda: datetime.now(timezone.utc)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

class Prompt(Base):

    __tablename__ = "prompts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    prompt_version: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    prompt_text: Mapped[str] = mapped_column(
        String(5000),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

class Rubric(Base):

    __tablename__ = "rubrics"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    rubric_version: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )
    
    rubric_definition: Mapped[dict] = mapped_column(
    JSON,
    nullable=False
    )
    
    technical_skills_max: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=20
    )

    competitive_achievement_max: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=15
    )

    relevant_experience_max: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=15
    )

    projects_max: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=25
    )

    demonstrated_potential_max: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=15
    )

    domain_relevance_max: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=10
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

class Evaluation(Base):

    __tablename__ = "evaluation"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    candidate_processing_id: Mapped[int] = mapped_column(
                            Integer,
                            ForeignKey("candidate_processing.id"),
                            nullable=False
    )

    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    prompt_version: Mapped[str] = mapped_column(
                    String(50),
                    nullable=False
    )

    rubric_version: Mapped[str] = mapped_column(
                    String(50),
                    nullable=False
    )

    technical_skills_score: Mapped[int] = mapped_column(
                            Integer,
                            nullable=False
    )

    technical_skills_evidence:  Mapped[list[str]] = mapped_column(
                                JSON,
                                nullable=False
    )

    technical_skills_reason: Mapped[str] = mapped_column(
                            String(2000),
                            nullable=False
    )

    competitive_achievement_score: Mapped[int] = mapped_column(
                                Integer,
                                nullable=False
    )

    competitive_achievement_evidence:Mapped[list[str]] = mapped_column(
    JSON,
    nullable=False
    )

    competitive_achievement_reason: Mapped[str] = mapped_column(
                                    String(2000),
                                    nullable=False
    )

    relevant_experience_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    relevant_experience_evidence:Mapped[list[str]] = mapped_column(
    JSON,
    nullable=False
    )

    relevant_experience_reason: Mapped[str] = mapped_column(
        String(2000),
        nullable=False
    )

    projects_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    projects_evidence:Mapped[list[str]] = mapped_column(
    JSON,
    nullable=False
    )

    projects_reason: Mapped[str] = mapped_column(
        String(2000),
        nullable=False
    )

    demonstrated_potential_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    demonstrated_potential_evidence:Mapped[list[str]] = mapped_column(
    JSON,
    nullable=False
    )

    demonstrated_potential_reason: Mapped[str] = mapped_column(
        String(2000),
        nullable=False
    )

    domain_relevance_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    domain_relevance_evidence:Mapped[list[str]]= mapped_column(
    JSON,
    nullable=False
    )

    domain_relevance_reason: Mapped[str] = mapped_column(
        String(2000),
        nullable=False
    )

    final_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

class ScreeningResult(Base):

    __tablename__ = "screening_result"
    
    __table_args__ = (
    UniqueConstraint("screening_id", "candidate_processing_id"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    screening_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("screening.id"),
        nullable=False
    )

    candidate_processing_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("candidate_processing.id"),
        nullable=False
    )

    evaluation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("evaluation.id"),
        nullable=False
    )

    final_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    result_status: Mapped[ScreeningResultStatus] = mapped_column(
    Enum(ScreeningResultStatus, name="screening_result_status"),
    nullable=False,
    default=ScreeningResultStatus.PENDING
    )

    rank: Mapped[int] = mapped_column(
        Integer,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

class ManualOverride(Base):

    __tablename__ = "manual_overrides"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    screening_result_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("screening_result.id"),
        nullable=False,
        index=True
    )

    previous_status: Mapped[ScreeningResultStatus] = mapped_column(
    Enum(ScreeningResultStatus, name="screening_result_status"),
    nullable=False
    )

    new_status: Mapped[ScreeningResultStatus] = mapped_column(
    Enum(ScreeningResultStatus, name="screening_result_status"),
    nullable=False
    )

    reason: Mapped[str] = mapped_column(
        String(1000),
        nullable=False
    )

    overridden_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user_master.id"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

