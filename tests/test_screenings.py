import uuid
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.deps import get_current_user
from app.services.screening_service import ScreeningService
from app.core.metrics import SCREENING_STARTS
from app.main import app
from app.db.database import SessionLocal
from app.db.models import (
    Candidate,
    CandidateProcessing,
    Domain,
    Evaluation,
    Hackathon,
    ManualOverride,
    Resume,
    Screening,
    ScreeningResult,
    ScreeningResultStatus,
    Team,
    TeamMember,
    User,
)

client = TestClient(app)


@pytest.fixture
def screening_test_data():
    db = SessionLocal()

    hackathon = Hackathon(
        name=f"Screening Test Hackathon {uuid.uuid4().hex}",
        description="Test hackathon",
    )
    db.add(hackathon)
    db.flush()

    domain = Domain(
        name="AI/ML",
        description="Python, machine learning, AI, data science",
        hackathon_id=hackathon.id,
    )
    db.add(domain)
    db.flush()

    candidate = Candidate(
        name="Screening Test Candidate",
        email=f"screening.{uuid.uuid4().hex}@example.com",
        college="Test College",
    )
    db.add(candidate)
    db.flush()

    team = Team(
        hackathon_id=hackathon.id,
        domain_id=domain.id,
        team_name=f"Test Team {uuid.uuid4().hex}",
    )
    db.add(team)
    db.flush()

    db.add(
        TeamMember(
            team_id=team.id,
            candidate_id=candidate.id,
            is_team_lead=True,
        )
    )

    db.add(
        Resume(
            candidate_id=candidate.id,
            resume_url="https://example.com/test-resume.pdf",
            file_type="pdf",
            file_size=100,
        )
    )

    db.commit()

    data = {
        "hackathon_id": hackathon.id,
        "domain_id": domain.id,
        "candidate_id": candidate.id,
        "team_id": team.id,
    }

    db.close()

    yield data

    db = SessionLocal()

    screening_ids = [
        screening.id
        for screening in db.query(Screening)
        .filter(Screening.hackathon_id == data["hackathon_id"])
        .all()
    ]

    if screening_ids:
        processing_ids = [
            processing.id
            for processing in db.query(CandidateProcessing)
            .filter(CandidateProcessing.screening_id.in_(screening_ids))
            .all()
        ]

        if processing_ids:
            db.query(CandidateProcessing).filter(
                CandidateProcessing.id.in_(processing_ids)
            ).delete(synchronize_session=False)

        db.query(Screening).filter(
            Screening.id.in_(screening_ids)
        ).delete(synchronize_session=False)

    db.query(TeamMember).filter(
        TeamMember.team_id == data["team_id"]
    ).delete(synchronize_session=False)

    db.query(Resume).filter(
        Resume.candidate_id == data["candidate_id"]
    ).delete(synchronize_session=False)

    db.query(Team).filter(
        Team.id == data["team_id"]
    ).delete(synchronize_session=False)

    db.query(Candidate).filter(
        Candidate.id == data["candidate_id"]
    ).delete(synchronize_session=False)

    db.query(Domain).filter(
        Domain.id == data["domain_id"]
    ).delete(synchronize_session=False)

    db.query(Hackathon).filter(
        Hackathon.id == data["hackathon_id"]
    ).delete(synchronize_session=False)

    db.commit()
    db.close()


def create_screening(data):
    response = client.post(
        "/api/v1/screenings",
        json={
            "hackathon_id": data["hackathon_id"],
            "domain_id": data["domain_id"],
            "selection_limit": 1,
            "waitlist_limit": 1,
        },
    )

    assert response.status_code == 201
    return response.json()


def test_create_screening(screening_test_data):
    screening = create_screening(screening_test_data)

    assert screening["hackathon_id"] == screening_test_data["hackathon_id"]
    assert screening["domain_id"] == screening_test_data["domain_id"]
    assert screening["selection_limit"] == 1
    assert screening["waitlist_limit"] == 1
    assert screening["status"] == "PENDING"


def test_get_screening(screening_test_data):
    screening = create_screening(screening_test_data)

    response = client.get(
        f"/api/v1/screenings/{screening['id']}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == screening["id"]
    assert data["status"] == "PENDING"


def test_list_screenings(screening_test_data):
    screening = create_screening(screening_test_data)

    response = client.get("/api/v1/screenings")

    assert response.status_code == 200

    screenings = response.json()

    assert isinstance(screenings, list)
    assert any(
        item["id"] == screening["id"]
        for item in screenings
    )


def test_start_screening_without_candidates():
    db = SessionLocal()

    hackathon = Hackathon(
        name=f"Empty Screening Hackathon {uuid.uuid4().hex}"
    )
    db.add(hackathon)
    db.flush()

    domain = Domain(
        name="Empty Domain",
        description="No candidates",
        hackathon_id=hackathon.id,
    )
    db.add(domain)
    db.commit()

    hackathon_id = hackathon.id
    domain_id = domain.id

    db.close()

    screening_id = None

    try:
        response = client.post(
            "/api/v1/screenings",
            json={
                "hackathon_id": hackathon_id,
                "domain_id": domain_id,
                "selection_limit": 1,
                "waitlist_limit": 1,
            },
        )

        assert response.status_code == 201

        screening_id = response.json()["id"]

        response = client.post(
            f"/api/v1/screenings/{screening_id}/start"
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "No candidates found for this hackathon/domain"
        )

    finally:
        db = SessionLocal()

        if screening_id:
            db.query(Screening).filter(
                Screening.id == screening_id
            ).delete(synchronize_session=False)

        db.query(Domain).filter(
            Domain.id == domain_id
        ).delete(synchronize_session=False)

        db.query(Hackathon).filter(
            Hackathon.id == hackathon_id
        ).delete(synchronize_session=False)

        db.commit()
        db.close()


def test_start_screening_creates_candidate_processing(
    screening_test_data,
):
    screening = create_screening(screening_test_data)
    starts_before = SCREENING_STARTS._value.get()

    # Prevent the real background workflow from running.
    with patch(
        "app.api.v1.screenings.run_screening"
    ):
        response = client.post(
            f"/api/v1/screenings/{screening['id']}/start"
        )

    assert response.status_code == 200
    assert SCREENING_STARTS._value.get() == starts_before + 1

    data = response.json()

    assert data["screening_id"] == screening["id"]
    assert data["status"] == "IN_PROGRESS"

    db = SessionLocal()

    processing = (
        db.query(CandidateProcessing)
        .filter(
            CandidateProcessing.screening_id == screening["id"],
            CandidateProcessing.candidate_id
            == screening_test_data["candidate_id"],
        )
        .first()
    )

    assert processing is not None

    db.close()

def test_manual_override_updates_result_and_creates_audit(
    screening_test_data,
):
    db = SessionLocal()

    # Create screening
    screening = Screening(
        hackathon_id=screening_test_data["hackathon_id"],
        domain_id=screening_test_data["domain_id"],
        selection_limit=1,
        waitlist_limit=1,
    )
    db.add(screening)
    db.flush()

    # Create candidate processing
    processing = CandidateProcessing(
        screening_id=screening.id,
        candidate_id=screening_test_data["candidate_id"],
    )
    db.add(processing)
    db.flush()

    # Create evaluation
    evaluation = Evaluation(
        candidate_processing_id=processing.id,
        model="test-model",
        prompt_version="test-v1",
        rubric_version="test-v1",
        evaluation_data={},
        technical_skills_score=10,
        competitive_achievement_score=10,
        relevant_experience_score=10,
        projects_score=10,
        demonstrated_potential_score=10,
        domain_relevance_score=10,
        final_score=60,
    )
    db.add(evaluation)
    db.flush()

    # Create screening result
    result = ScreeningResult(
        screening_id=screening.id,
        candidate_processing_id=processing.id,
        evaluation_id=evaluation.id,
        final_score=60,
        result_status=ScreeningResultStatus.SELECTED,
        rank=1,
    )
    db.add(result)

    # Create user who performs the override
    user = User(
        name="Override Tester",
        email=f"override.{uuid.uuid4().hex}@example.com",
        hashed_password="test-hash",
    )
    db.add(user)

    db.commit()

    result_id = result.id
    screening_id = screening.id
    user_id = user.id

    try:
        service = ScreeningService(db)

        updated_result = service.manual_override(
            screening_id=screening_id,
            result_id=result_id,
            new_status=ScreeningResultStatus.REJECTED,
            reason="Manual review changed the decision",
            user_id=user_id,
        )

        assert updated_result.result_status == ScreeningResultStatus.REJECTED

        override = (
            db.query(ManualOverride)
            .filter(
                ManualOverride.screening_result_id == result_id
            )
            .first()
        )

        assert override is not None
        assert override.previous_status == ScreeningResultStatus.SELECTED
        assert override.new_status == ScreeningResultStatus.REJECTED
        assert override.reason == "Manual review changed the decision"
        assert override.overridden_by == user_id

    finally:
        db.query(ManualOverride).filter(
            ManualOverride.screening_result_id == result_id
        ).delete(synchronize_session=False)

        db.query(ScreeningResult).filter(
            ScreeningResult.id == result_id
        ).delete(synchronize_session=False)

        db.query(Evaluation).filter(
            Evaluation.id == evaluation.id
        ).delete(synchronize_session=False)

        db.query(CandidateProcessing).filter(
            CandidateProcessing.id == processing.id
        ).delete(synchronize_session=False)

        db.query(User).filter(
            User.id == user_id
        ).delete(synchronize_session=False)

        db.query(Screening).filter(
            Screening.id == screening_id
        ).delete(synchronize_session=False)

        db.commit()
        db.close()


def test_manual_override_rejects_empty_reason(screening_test_data):
    db = SessionLocal()

    screening = Screening(
        hackathon_id=screening_test_data["hackathon_id"],
        domain_id=screening_test_data["domain_id"],
        selection_limit=1,
        waitlist_limit=1,
    )
    db.add(screening)
    db.flush()

    processing = CandidateProcessing(
        screening_id=screening.id,
        candidate_id=screening_test_data["candidate_id"],
    )
    db.add(processing)
    db.flush()

    evaluation = Evaluation(
        candidate_processing_id=processing.id,
        model="test-model",
        prompt_version="test-v1",
        rubric_version="test-v1",
        evaluation_data={},
        technical_skills_score=10,
        competitive_achievement_score=10,
        relevant_experience_score=10,
        projects_score=10,
        demonstrated_potential_score=10,
        domain_relevance_score=10,
        final_score=60,
    )
    db.add(evaluation)
    db.flush()

    result = ScreeningResult(
        screening_id=screening.id,
        candidate_processing_id=processing.id,
        evaluation_id=evaluation.id,
        final_score=60,
        result_status=ScreeningResultStatus.SELECTED,
        rank=1,
    )
    db.add(result)
    db.commit()

    try:
        service = ScreeningService(db)

        with pytest.raises(HTTPException) as exc:
            service.manual_override(
                screening_id=screening.id,
                result_id=result.id,
                new_status=ScreeningResultStatus.REJECTED,
                reason="   ",
                user_id=1,
            )

        assert exc.value.status_code == 400
        assert exc.value.detail == "Override reason is required"

    finally:
        db.query(ScreeningResult).filter(
            ScreeningResult.id == result.id
        ).delete(synchronize_session=False)

        db.query(Evaluation).filter(
            Evaluation.id == evaluation.id
        ).delete(synchronize_session=False)

        db.query(CandidateProcessing).filter(
            CandidateProcessing.id == processing.id
        ).delete(synchronize_session=False)

        db.query(Screening).filter(
            Screening.id == screening.id
        ).delete(synchronize_session=False)

        db.commit()
        db.close()

def test_manual_override_rejects_same_status(screening_test_data):
    db = SessionLocal()

    screening = Screening(
        hackathon_id=screening_test_data["hackathon_id"],
        domain_id=screening_test_data["domain_id"],
        selection_limit=1,
        waitlist_limit=1,
    )
    db.add(screening)
    db.flush()

    processing = CandidateProcessing(
        screening_id=screening.id,
        candidate_id=screening_test_data["candidate_id"],
    )
    db.add(processing)
    db.flush()

    evaluation = Evaluation(
        candidate_processing_id=processing.id,
        model="test-model",
        prompt_version="test-v1",
        rubric_version="test-v1",
        evaluation_data={},
        technical_skills_score=10,
        competitive_achievement_score=10,
        relevant_experience_score=10,
        projects_score=10,
        demonstrated_potential_score=10,
        domain_relevance_score=10,
        final_score=60,
    )
    db.add(evaluation)
    db.flush()

    result = ScreeningResult(
        screening_id=screening.id,
        candidate_processing_id=processing.id,
        evaluation_id=evaluation.id,
        final_score=60,
        result_status=ScreeningResultStatus.SELECTED,
        rank=1,
    )
    db.add(result)
    db.commit()

    try:
        service = ScreeningService(db)

        with pytest.raises(HTTPException) as exc:
            service.manual_override(
                screening_id=screening.id,
                result_id=result.id,
                new_status=ScreeningResultStatus.SELECTED,
                reason="Manual review",
                user_id=1,
            )

        assert exc.value.status_code == 400
        assert exc.value.detail == (
            "New status must be different from the current status"
        )

    finally:
        db.query(ScreeningResult).filter(
            ScreeningResult.id == result.id
        ).delete(synchronize_session=False)

        db.query(Evaluation).filter(
            Evaluation.id == evaluation.id
        ).delete(synchronize_session=False)

        db.query(CandidateProcessing).filter(
            CandidateProcessing.id == processing.id
        ).delete(synchronize_session=False)

        db.query(Screening).filter(
            Screening.id == screening.id
        ).delete(synchronize_session=False)

        db.commit()
        db.close()

def test_manual_override_api_updates_result_and_creates_audit(
    screening_test_data,
):
    db = SessionLocal()

    screening = Screening(
        hackathon_id=screening_test_data["hackathon_id"],
        domain_id=screening_test_data["domain_id"],
        selection_limit=1,
        waitlist_limit=1,
    )
    db.add(screening)
    db.flush()

    processing = CandidateProcessing(
        screening_id=screening.id,
        candidate_id=screening_test_data["candidate_id"],
    )
    db.add(processing)
    db.flush()

    evaluation = Evaluation(
        candidate_processing_id=processing.id,
        model="test-model",
        prompt_version="test-v1",
        rubric_version="test-v1",
        evaluation_data={},
        technical_skills_score=10,
        competitive_achievement_score=10,
        relevant_experience_score=10,
        projects_score=10,
        demonstrated_potential_score=10,
        domain_relevance_score=10,
        final_score=60,
    )
    db.add(evaluation)
    db.flush()

    result = ScreeningResult(
        screening_id=screening.id,
        candidate_processing_id=processing.id,
        evaluation_id=evaluation.id,
        final_score=60,
        result_status=ScreeningResultStatus.SELECTED,
        rank=1,
    )
    db.add(result)

    user = User(
        name="API Override Tester",
        email=f"api.override.{uuid.uuid4().hex}@example.com",
        hashed_password="test-hash",
    )
    db.add(user)

    db.commit()

    screening_id = screening.id
    result_id = result.id
    user_id = user.id

    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        id=user_id,
        role=SimpleNamespace(value="ADMIN"),
    )

    try:
        response = client.patch(
            f"/api/v1/screenings/{screening_id}/results/{result_id}/override",
            json={
                "new_status": "REJECTED",
                "reason": "Manual API review changed the decision",
            },
        )

        assert response.status_code == 200

        db.refresh(result)

        assert result.result_status == ScreeningResultStatus.REJECTED

        override = (
            db.query(ManualOverride)
            .filter(
                ManualOverride.screening_result_id == result_id
            )
            .first()
        )

        assert override is not None
        assert override.previous_status == ScreeningResultStatus.SELECTED
        assert override.new_status == ScreeningResultStatus.REJECTED
        assert override.reason == "Manual API review changed the decision"
        assert override.overridden_by == user_id

    finally:
        app.dependency_overrides.clear()

        db.query(ManualOverride).filter(
            ManualOverride.screening_result_id == result_id
        ).delete(synchronize_session=False)

        db.query(ScreeningResult).filter(
            ScreeningResult.id == result_id
        ).delete(synchronize_session=False)

        db.query(Evaluation).filter(
            Evaluation.id == evaluation.id
        ).delete(synchronize_session=False)

        db.query(CandidateProcessing).filter(
            CandidateProcessing.id == processing.id
        ).delete(synchronize_session=False)

        db.query(User).filter(
            User.id == user_id
        ).delete(synchronize_session=False)

        db.query(Screening).filter(
            Screening.id == screening_id
        ).delete(synchronize_session=False)

        db.commit()
        db.close()

def test_manual_override_api_requires_authentication():
    response = client.patch(
        "/api/v1/screenings/1/results/1/override",
        json={
            "new_status": "REJECTED",
            "reason": "Manual review",
        },
    )

    assert response.status_code == 401

def test_manual_override_api_rejects_unauthorized_role():
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        id=1,
        role=SimpleNamespace(value="UNAUTHORIZED"),
    )

    try:
        response = client.patch(
            "/api/v1/screenings/1/results/1/override",
            json={
                "new_status": "REJECTED",
                "reason": "Manual review",
            },
        )

        assert response.status_code == 403

    finally:
        app.dependency_overrides.clear()
