# backend/tests/test_status.py

from app import app

def test_status_endpoint():
    client = app.test_client()
    response = client.get("/api/status")

    assert response.status_code == 200
    assert response.json["status"] == "ok"