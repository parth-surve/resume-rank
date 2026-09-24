import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import SessionLocal
from app.db.models import Candidate


client = TestClient(app)

TEST_EMAIL = "test.candidate.api@example.com"


@pytest.fixture(autouse=True)
def cleanup_test_candidate():
    yield

    db = SessionLocal()

    candidate = (
        db.query(Candidate)
        .filter(Candidate.email == TEST_EMAIL)
        .first()
    )

    if candidate:
        db.delete(candidate)
        db.commit()

    db.close()


def create_test_candidate():
    response = client.post(
        "/api/v1/candidates",
        json={
            "name": "Test Candidate",
            "email": TEST_EMAIL,
            "mobile": "9876543210",
            "college": "Test College",
            "linkedin_url": "https://linkedin.com/in/test",
            "github_url": "https://github.com/test",
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_candidate():
    candidate = create_test_candidate()

    assert candidate["name"] == "Test Candidate"
    assert candidate["email"] == TEST_EMAIL


def test_get_candidate():
    candidate = create_test_candidate()

    response = client.get(
        f"/api/v1/candidates/{candidate['id']}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == candidate["id"]
    assert data["email"] == TEST_EMAIL


def test_list_candidates():
    create_test_candidate()

    response = client.get("/api/v1/candidates")

    assert response.status_code == 200

    candidates = response.json()

    assert isinstance(candidates, list)
    assert any(
        candidate["email"] == TEST_EMAIL
        for candidate in candidates
    )


def test_duplicate_candidate_email():
    create_test_candidate()

    response = client.post(
        "/api/v1/candidates",
        json={
            "name": "Duplicate Candidate",
            "email": TEST_EMAIL,
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Candidate with this email already exists"
    )