from datetime import datetime
from sqlalchemy import String, DateTime, func, Integer,UniqueConstraint,Float
from sqlalchemy.orm import Mapped, mapped_column
import enum
from sqlalchemy import Enum as SQLEnum

from app.db.database import Base


class Hackathon(Base):
    __tablename__ = "hackathons"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
from sqlalchemy import ForeignKey

class Domain(Base):
    __tablename__ = "domains"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    
class Import(Base):
    __tablename__ = "imports"
    id:Mapped[int] = map
    id: Mapped[int] = mapped_column(primary_key=True)
    hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons.id"))
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id"))
    filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    
class ScreeningStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    
class ProcessingStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class FinalDecision(str, enum.Enum):
    SELECTED = "SELECTED"
    WAITLIST = "WAITLIST"
    REJECTED = "REJECTED"
    
class Screening(Base):
    __tablename__ = "screenings"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons_id"))
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains_id"))
    
    selection_limit: Mapped[int] = mapped_column(Integer)
    waitlist_limit: Mapped[int] = mapped_column(Integer)
    rubric_version: Mapped[str] = mapped_column(String(50))

    status: Mapped[ScreeningStatus] = mapped_column(SQLEnum(ScreeningStatus), default=ScreeningStatus.PENDING)
    
    total: Mapped[int] = mapped_column(Integer, default=0)
    processed: Mapped[int] = mapped_column(Integer, default=0)
    successful: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    
class Candidate(Base):
    __tablename__ = "candidates"
    __table_args__ = (
        UniqueConstraint("hackathon_id", "domain_id", "email", name="uq_candidate_per_domain"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    hackathon_id: Mapped[int] = mapped_column(ForeignKey("hackathons.id"))
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id"))

    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
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