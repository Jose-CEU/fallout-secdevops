import json
import pytest
from app import app, init_db

@pytest.fixture(autouse=True)
def setup_db():
    with app.app_context():
        init_db()

def test_register():
    client = app.test_client()
    response = client.post(
        "/api/register",
        data=json.dumps({
            "username": "testuser_auth",
            "password": "testpass"
        }),
        content_type="application/json"
    )
    assert response.status_code in [201, 409]

def test_login():
    client = app.test_client()
    response = client.post(
        "/api/login",
        data=json.dumps({
            "username": "overseer",
            "password": "overseer_admin_2024"
        }),
        content_type="application/json"
    )
    assert response.status_code == 200