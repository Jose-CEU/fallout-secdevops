from app import app

def test_api_status():
    client = app.test_client()
    response = client.get("/api/status")
    assert response.status_code == 200