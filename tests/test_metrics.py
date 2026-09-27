from fastapi.testclient import TestClient

from app.main import app


def test_metrics_endpoint_exposes_http_metrics_without_self_observation():
    client = TestClient(app)
    client.get("/")
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "resumerank_http_requests_total" in response.text
    assert "resumerank_http_request_duration_seconds" in response.text
    assert 'path="/"' in response.text
    assert 'path="/metrics"' not in response.text
