import asyncio
import io
import uuid
from unittest.mock import patch
import openpyxl
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import SessionLocal
from app.db.models import (
    Candidate,
    CandidateProcessing,
    CandidateProcessingStatus,
    Domain,
    Evaluation,
    Hackathon,
    ManualOverride,
    ProcessingFailure,
    ProcessingStage,
    Resume,
    Screening,
    ScreeningResult,
    ScreeningResultStatus,
    ScreeningStatus,
    Team,
    TeamMember,
    User,
    UserRole,
)
from app.core.security import hash_password, create_access_token
from app.workflows.screening_workflow import run_screening
from ai.schemas import CandidateEvaluation

client = TestClient(app)


def make_mock_ai_eval(total_score: int) -> dict:
    """Construct mock AI result with structured subcriteria."""
    eval_model = CandidateEvaluation.model_validate({
        "technical_skills": {
            "skill_match": {"score": 6},
            "proficiency_evidence": {"score": 5},
            "technical_depth": {"score": 3},
        },
        "competitive_achievement": {
            "score": 5,
        },
        "relevant_experience": {
            "relevance_and_responsibility": {"score": 4},
            "technical_depth": {"score": 3},
            "evidence_and_impact": {"score": 2},
        },
        "projects": {
            "technical_complexity_and_depth": {"score": 6},
            "ownership_and_implementation": {"score": 5},
            "relevance_and_problem_solving": {"score": 4},
            "evidence_of_outcomes": {"score": 2},
        },
        "demonstrated_potential": {
            "learning_and_growth": {"score": 3},
            "initiative_and_ownership": {"score": 3},
            "evidence_of_trajectory": {"score": 2},
        },
        "domain_relevance": {
            "domain_alignment": {"score": 5},
        },
    })

    return {
        "evaluation": eval_model,
        "scores": {
            "technical_skills": 14,
            "competitive_achievement": 5,
            "relevant_experience": 9,
            "projects": 17,
            "demonstrated_potential": 8,
            "domain_relevance": 5,
            "total_score": total_score,
        },
        "metadata": {
            "prompt_version": "v1",
            "provider": "groq",
            "model": "qwen/qwen3.8-27b",
        },
    }


def test_full_e2e_screening_workflow_and_export():
    db = SessionLocal()

    # 1. Setup Admin User for Auth
    user_email = f"admin.{uuid.uuid4().hex}@example.com"
    admin_user = User(
        name="Admin Test",
        email=user_email,
        hashed_password=hash_password("adminpass123"),
        role=UserRole.ADMIN,
    )
    db.add(admin_user)
    db.flush()

    token = create_access_token(admin_user.id, admin_user.role.value)
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Setup Hackathon and Domain
    hackathon = Hackathon(
        name=f"E2E Hackathon {uuid.uuid4().hex}",
        description="End to end test hackathon",
    )
    db.add(hackathon)
    db.flush()

    domain = Domain(
        name="AI Track",
        description="Python, PyTorch, LLMs, NLP",
        hackathon_id=hackathon.id,
    )
    db.add(domain)
    db.flush()

    # 3. Setup Candidates: 3 candidates (1 top, 1 mid, 1 failing download)
    c1 = Candidate(name="Top Candidate", email=f"c1.{uuid.uuid4().hex}@example.com", college="MIT")
    c2 = Candidate(name="Mid Candidate", email=f"c2.{uuid.uuid4().hex}@example.com", college="Stanford")
    c3 = Candidate(name="Broken Resume Candidate", email=f"c3.{uuid.uuid4().hex}@example.com", college="Harvard")
    db.add_all([c1, c2, c3])
    db.flush()

    r1 = Resume(candidate_id=c1.id, resume_url="https://example.com/c1.pdf", file_type="pdf", file_size=100)
    r2 = Resume(candidate_id=c2.id, resume_url="https://example.com/c2.pdf", file_type="pdf", file_size=100)
    r3 = Resume(candidate_id=c3.id, resume_url="https://example.com/broken.pdf", file_type="pdf", file_size=100)
    db.add_all([r1, r2, r3])
    db.flush()

    team = Team(hackathon_id=hackathon.id, domain_id=domain.id, team_name=f"Team {uuid.uuid4().hex}")
    db.add(team)
    db.flush()

    db.add_all([
        TeamMember(team_id=team.id, candidate_id=c1.id, is_team_lead=True),
        TeamMember(team_id=team.id, candidate_id=c2.id, is_team_lead=False),
        TeamMember(team_id=team.id, candidate_id=c3.id, is_team_lead=False),
    ])
    db.commit()

    hackathon_id = hackathon.id
    domain_id = domain.id
    user_id = admin_user.id
    c1_id = c1.id
    c2_id = c2.id
    c3_id = c3.id
    team_id = team.id
    db.close()

    screening_id = None
    try:
        # 4. Create Screening via API (selection_limit=1, waitlist_limit=1)
        create_res = client.post("/api/v1/screenings", json={
            "hackathon_id": hackathon_id,
            "domain_id": domain_id,
            "selection_limit": 1,
            "waitlist_limit": 1,
        })
        assert create_res.status_code == 201
        screening_id = create_res.json()["id"]

        # 5. Define mocks for resume download and AI evaluation
        def mock_download(url: str, **kwargs):
            if "c1.pdf" in url:
                return {"success": True, "resume_text": "Top candidate resume text with Python"}
            elif "c2.pdf" in url:
                return {"success": True, "resume_text": "Mid candidate resume text with SQL"}
            else:
                return {"success": False, "resume_text": "", "reason": "Simulated PDF network failure"}

        def mock_eval(resume_text, **kwargs):
            if "Top candidate" in resume_text:
                return make_mock_ai_eval(88)
            else:
                return make_mock_ai_eval(65)

        # 6. Start Screening via API (executes background screening task with mocks in TestClient)
        with patch("app.workflows.screening_workflow.download_resume_in_memory", side_effect=mock_download), \
             patch("app.workflows.screening_workflow.evaluate_candidate", side_effect=mock_eval):
            start_res = client.post(f"/api/v1/screenings/{screening_id}/start")
            assert start_res.status_code == 200
            assert start_res.json()["status"] == "IN_PROGRESS"

        # 7. Check screening details via API
        get_scr = client.get(f"/api/v1/screenings/{screening_id}")
        assert get_scr.status_code == 200
        scr_data = get_scr.json()
        assert scr_data["status"] == "COMPLETED"
        assert scr_data["total_candidates"] == 3
        assert scr_data["processed_candidates"] == 2
        assert scr_data["failed_candidates"] == 1

        # 8. Check results via API
        res_list = client.get(f"/api/v1/screenings/{screening_id}/results")
        assert res_list.status_code == 200
        items = res_list.json()["items"]
        assert len(items) == 2

        # Candidate 1 should be rank 1 and SELECTED
        top_item = items[0]
        assert top_item["candidate_id"] == c1_id
        assert top_item["rank"] == 1
        assert top_item["final_score"] == 88
        assert top_item["result_status"] == "SELECTED"

        # Candidate 2 should be rank 2 and WAITLISTED
        mid_item = items[1]
        assert mid_item["candidate_id"] == c2_id
        assert mid_item["rank"] == 2
        assert mid_item["final_score"] == 65
        assert mid_item["result_status"] == "WAITLISTED"

        # 9. Check failures via API
        fail_res = client.get(f"/api/v1/screenings/{screening_id}/failures")
        assert fail_res.status_code == 200
        failures = fail_res.json()
        assert len(failures) == 1
        assert failures[0]["stage"] == "EXTRACTION"
        assert "Simulated PDF network failure" in failures[0]["error_message"]

        # 10. Test Manual Override: Change rank 2 from WAITLISTED to SELECTED
        db_check = SessionLocal()
        res2_id = db_check.query(ScreeningResult.id).filter(
            ScreeningResult.screening_id == screening_id,
            ScreeningResult.rank == 2,
        ).scalar()
        db_check.close()

        override_res = client.patch(
            f"/api/v1/screenings/{screening_id}/results/{res2_id}/override",
            json={"new_status": "SELECTED", "reason": "Organizer manual approval"},
            headers=headers,
        )
        assert override_res.status_code == 200

        # Verify updated status
        res_list_after = client.get(f"/api/v1/screenings/{screening_id}/results")
        updated_items = res_list_after.json()["items"]
        assert updated_items[1]["result_status"] == "SELECTED"

        # 11. Test Export Endpoint
        export_res = client.get(f"/api/v1/screenings/{screening_id}/export")
        assert export_res.status_code == 200
        assert export_res.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        wb = openpyxl.load_workbook(io.BytesIO(export_res.content))
        assert "Screening Results" in wb.sheetnames
        assert "Summary" in wb.sheetnames

        ws = wb["Screening Results"]
        assert ws.max_row == 4  # Header + 3 candidates (2 evaluated + 1 failed)

    finally:
        # Cleanup
        db = SessionLocal()
        if screening_id:
            db.query(ManualOverride).filter(
                ManualOverride.screening_result_id.in_(
                    db.query(ScreeningResult.id).filter(ScreeningResult.screening_id == screening_id)
                )
            ).delete(synchronize_session=False)

            db.query(ScreeningResult).filter(ScreeningResult.screening_id == screening_id).delete(synchronize_session=False)
            db.query(Evaluation).filter(
                Evaluation.candidate_processing_id.in_(
                    db.query(CandidateProcessing.id).filter(CandidateProcessing.screening_id == screening_id)
                )
            ).delete(synchronize_session=False)
            db.query(ProcessingFailure).filter(
                ProcessingFailure.candidate_processing_id.in_(
                    db.query(CandidateProcessing.id).filter(CandidateProcessing.screening_id == screening_id)
                )
            ).delete(synchronize_session=False)
            db.query(CandidateProcessing).filter(CandidateProcessing.screening_id == screening_id).delete(synchronize_session=False)
            db.query(Screening).filter(Screening.id == screening_id).delete(synchronize_session=False)

        db.query(TeamMember).filter(TeamMember.team_id == team_id).delete(synchronize_session=False)
        db.query(Team).filter(Team.id == team_id).delete(synchronize_session=False)
        db.query(Resume).filter(Resume.candidate_id.in_([c1_id, c2_id, c3_id])).delete(synchronize_session=False)
        db.query(Candidate).filter(Candidate.id.in_([c1_id, c2_id, c3_id])).delete(synchronize_session=False)
        db.query(Domain).filter(Domain.id == domain_id).delete(synchronize_session=False)
        db.query(Hackathon).filter(Hackathon.id == hackathon_id).delete(synchronize_session=False)
        db.query(User).filter(User.id == user_id).delete(synchronize_session=False)
        db.commit()
        db.close()
