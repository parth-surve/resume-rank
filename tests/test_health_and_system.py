from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ResumeRank"


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "ResumeRank Backend is running"}


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "resumerank_http_requests_total" in response.text
