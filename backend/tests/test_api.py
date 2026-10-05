import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["active_districts_count"] == 10


def test_parse_api_endpoint():
    payload = {
        "text": "Київ — загроза балістики з півночі!",
        "source_channel": "@monitor_war"
    }
    response = client.post("/api/v1/parse", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["threat_event"] is not None
    assert data["threat_event"]["threat_type"] == "BALLISTIC"
    assert data["parse_time_ms"] < 10.0


def test_evaluate_api_endpoint():
    threat_payload = {
        "event_id": "evt_test_uav",
        "threat_type": "UAV_SHAHED",
        "scope": "SPATIAL_POLYGON",
        "urgency": "CRITICAL",
        "title": "БПЛА на Оболонь",
        "description": "Шахед курсом на Оболонь",
        "target_districts": ["Obolonskyi"],
        "timestamp_utc": 123456789
    }
    eval_req = {
        "threat_event": threat_payload,
        "user_districts": ["Obolonskyi"],
        "user_location": {"lat": 50.505, "lon": 30.498},
        "ballistics_enabled": True
    }
    response = client.post("/api/v1/evaluate", json=eval_req)
    assert response.status_code == 200
    data = response.json()
    assert data["action"] == "TRIGGER_DISTRICT_ALARM"


def test_districts_api_endpoint():
    response = client.get("/api/v1/districts")
    assert response.status_code == 200
    data = response.json()
    assert len(data["districts"]) == 10
    assert len(data["suburbs"]) >= 8
