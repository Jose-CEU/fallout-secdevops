import pytest
from app import app, init_db

@pytest.fixture(autouse=True)
def setup_db():
    with app.app_context():
        init_db()

def test_api_status():
    client = app.test_client()
    response = client.get("/api/status")
    assert response.status_code == 200

def test_register_and_login():
    client = app.test_client()

    response = client.post("/api/register",
        json={"username": "vaultdweller2", "password": "secure123"},
        content_type="application/json"
    )
    assert response.status_code in [201, 409]

    response = client.post("/api/login",
        json={"username": "vaultdweller2", "password": "secure123"},
        content_type="application/json"
    )
    assert response.status_code == 200

def test_login_wrong_password():
    client = app.test_client()
    response = client.post("/api/login",
        json={"username": "overseer", "password": "wrongpass"},
        content_type="application/json"
    )
    assert response.status_code == 401