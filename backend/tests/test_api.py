import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

client = TestClient(app)

def test_analyze_logs_success():
    response = client.post("/api/v1/analyze-logs", json={
        "logs": "Sample log data",
        "platform": "iOS",
        "language": "Swift"
    })
    assert response.status_code == 202
    data = response.json()
    assert "analysis_id" in data
    assert data["status"] == "QUEUED"

def test_analyze_logs_missing_data():
    response = client.post("/api/v1/analyze-logs", json={
        "platform": "iOS",
        "language": "Swift"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Either 'logs' or 'code_snippet' must be provided."

def test_get_analysis_status_not_found():
    response = client.get("/api/v1/status/non-existent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Analysis ID not found or expired"

def test_get_analysis_status_success():
    post_response = client.post("/api/v1/analyze-logs", json={
        "logs": "Sample log data",
        "platform": "iOS",
        "language": "Swift"
    })
    assert post_response.status_code == 202
    analysis_id = post_response.json()["analysis_id"]

    get_response = None
    for _ in range(5):
        get_response = client.get(f"/api/v1/status/{analysis_id}")
        if get_response.status_code == 200:
            break
        import time
        time.sleep(0.5)
    assert get_response is not None
    assert get_response.status_code == 200
    status_data = get_response.json()
    assert status_data["status"] in ["QUEUED", "IN_PROGRESS", "COMPLETED", "FAILED"]

    if status_data["status"] == "COMPLETED":
        assert "predicted_bugs" in status_data
        assert "suggested_patches" in status_data
