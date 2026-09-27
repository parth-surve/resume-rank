import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import SessionLocal
from app.db.models import (
    Candidate,
    CandidateProcessing,
    Domain,
    Hackathon,
    Resume,
    Screening,
    Team,
    TeamMember,
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

    # Prevent the real background workflow from running.
    with patch(
        "app.api.v1.screenings.run_screening"
    ):
        response = client.post(
            f"/api/v1/screenings/{screening['id']}/start"
        )

    assert response.status_code == 200

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