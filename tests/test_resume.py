import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import SessionLocal
from app.db.models import Candidate, Resume

client = TestClient(app)

TEST_EMAIL = "test.resume.api@example.com"

@pytest.fixture(autouse=True)
def cleanup_test_data():
    yield

    db = SessionLocal()

    candidate = (
        db.query(Candidate)
        .filter(Candidate.email == TEST_EMAIL)
        .first()
    )

    if candidate:
        resumes = (
            db.query(Resume)
            .filter(Resume.candidate_id == candidate.id)
            .all()
        )

        for resume in resumes:
            db.delete(resume)

        # Delete resumes first and commit before deleting candidate
        db.commit()

        db.delete(candidate)
        db.commit()

    db.close()


def create_test_candidate():
    response = client.post(
        "/api/v1/candidates",
        json={
            "name": "Resume Test Candidate",
            "email": TEST_EMAIL,
            "college": "Test College",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_test_resume(candidate_id):
    response = client.post(
        "/api/v1/resumes",
        json={
            "candidate_id": candidate_id,
            "resume_url": "https://example.com/test-resume.pdf",
            "file_type": "pdf",
            "file_size": 123456,
        },
    )

    assert response.status_code == 201
    return response.json()


def test_create_resume():
    candidate = create_test_candidate()

    resume = create_test_resume(candidate["id"])

    assert resume["candidate_id"] == candidate["id"]
    assert resume["resume_url"] == (
        "https://example.com/test-resume.pdf"
    )
    assert resume["file_type"] == "pdf"
    assert resume["file_size"] == 123456
    assert resume["extraction_status"] == "PENDING"


def test_get_resume():
    candidate = create_test_candidate()
    resume = create_test_resume(candidate["id"])

    response = client.get(
        f"/api/v1/resumes/{resume['id']}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == resume["id"]
    assert data["candidate_id"] == candidate["id"]


def test_list_candidate_resumes():
    candidate = create_test_candidate()

    resume1 = create_test_resume(candidate["id"])
    resume2 = create_test_resume(candidate["id"])

    response = client.get(
        f"/api/v1/resumes/candidate/{candidate['id']}"
    )

    assert response.status_code == 200

    resumes = response.json()

    assert len(resumes) == 2
    assert resumes[0]["id"] == resume1["id"]
    assert resumes[1]["id"] == resume2["id"]


def test_create_resume_invalid_candidate():
    response = client.post(
        "/api/v1/resumes",
        json={
            "candidate_id": 99999,
            "resume_url": "https://example.com/test.pdf",
            "file_type": "pdf",
            "file_size": 1000,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Candidate not found"


def test_list_resumes_invalid_candidate():
    response = client.get(
        "/api/v1/resumes/candidate/99999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Candidate not found"