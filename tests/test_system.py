from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "nlp_request_count_total" in response.text

# We don't test /generate here to avoid downloading/loading the full GPT-2 model in simple tests,
# or we could mock it. For now, simple tests to ensure the API starts and basic endpoints work.
