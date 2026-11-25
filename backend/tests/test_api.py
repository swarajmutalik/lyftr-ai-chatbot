
import uuid

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["keys_configured"] >= 2
    assert data["cache_enabled"] is True


def test_empty_message():
    response = client.post(
        "/chat",
        json={
            "session_id": "test-session",
            "message": ""
        }
    )

    assert response.status_code == 422


def test_missing_session_id():
    response = client.post(
        "/chat",
        json={
            "message": "Hello"
        }
    )

    assert response.status_code == 422


def test_message_too_long():
    response = client.post(
        "/chat",
        json={
            "session_id": "test-session",
            "message": "a" * 4001
        }
    )

    assert response.status_code == 422


def test_unknown_session():
    session_id = f"missing-{uuid.uuid4()}"

    response = client.get(
        f"/sessions/{session_id}/messages"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "session not found"
    )
