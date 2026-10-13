"""FastAPI route smoke tests and error mapping."""
import os
os.environ.setdefault("AUDIT_SECRET_KEY", "test-only-api-signing-key-1234567890")
from fastapi.testclient import TestClient
from agents.api import app


def test_api_core_routes():
    client = TestClient(app)
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "HEALTHY"
    payload = {"task_id": "API-T1", "target_identifier": "DRAM-01",
               "primary_metric": 35, "secondary_metric": 1, "status_descriptor": "NOMINAL"}
    result = client.post("/api/audit", json=payload)
    assert result.status_code == 200, result.text
    assert result.json()["overall_urgency"] == "ELEVATED_RISK"
    assert client.get("/api/audit/logs").json()["verified"] is True
    assert client.get("/metrics").json()["dossiers_processed_total"] >= 1
    assert client.get("/openapi.json").status_code == 200


def test_api_rejects_sensitive_identifiers_without_500():
    client = TestClient(app)
    response = client.post("/api/audit", json={
        "task_id": "MRN-123456", "target_identifier": "DRAM-01",
        "primary_metric": 3.0,
    })
    assert response.status_code == 400
