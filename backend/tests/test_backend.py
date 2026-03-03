import requests

def test_api_status():
    response = requests.get("http://localhost:5001/api/status")
    assert response.status_code == 200
    assert "vault_status" in response.json()