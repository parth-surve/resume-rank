from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import Domain, Hackathon, Import
from app.schemas.imports import ImportCreate, ImportOut

from data_pipeline.pipeline_runner import run_pipeline
from app.services.candidate_ingestion_service import CandidateIngestionService


class ImportService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: ImportCreate) -> ImportOut:
        # 1. Validate hackathon
        hackathon = (
            self.db.query(Hackathon)
            .filter(Hackathon.id == payload.hackathon_id)
            .first()
        )

        if not hackathon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hackathon not found",
            )

        # 2. Validate domain belongs to the hackathon
        domain = (
            self.db.query(Domain)
            .filter(
                Domain.id == payload.domain_id,
                Domain.hackathon_id == payload.hackathon_id,
            )
            .first()
        )

        if not domain:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Domain not found for this hackathon",
            )

        # 3. Create import record
        record = Import(
            hackathon_id=payload.hackathon_id,
            domain_id=payload.domain_id,
            filename=payload.filename,
            file_path=payload.file_path,
        )

        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        # 4. Run the data pipeline on the uploaded Excel file
        try:
            valid_df, failed_df, downloaded_resumes = run_pipeline(
                payload.file_path
            )

            # 5. Save valid candidates and resumes to PostgreSQL
            created_candidates, created_resumes = (
                CandidateIngestionService(self.db).ingest_candidates(
                    valid_df
                )
            )

            print(
                f"Import {record.id}: "
                f"{len(valid_df)} valid candidates, "
                f"{len(failed_df)} failed candidates, "
                f"{len(downloaded_resumes)} resumes processed, "
                f"{len(created_candidates)} candidates created, "
                f"{len(created_resumes)} resumes created."
            )

        except Exception as pipeline_error:
            print(
                f"Import {record.id}: "
                f"Pipeline failed: {pipeline_error}"
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process imported Excel file",
            )

        # 6. Return import record
        return ImportOut.model_validate(record)

    def get(self, import_id: int) -> ImportOut:
        record = (
            self.db.query(Import)
            .filter(Import.id == import_id)
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Import not found",
            )

        return ImportOut.model_validate(record)

    def list(self, hackathon_id: int) -> list[ImportOut]:
        records = (
            self.db.query(Import)
            .filter(Import.hackathon_id == hackathon_id)
            .all()
        )

        return [
            ImportOut.model_validate(record)
            for record in records
        ]