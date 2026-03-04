import json
from app import app

def test_register():
    client = app.test_client()

    response = client.post(
        "/api/register",
        data=json.dumps({
            "username": "testuser",
            "password": "testpass"
        }),
        content_type="application/json"
    )

    assert response.status_code == 201


def test_login():
    client = app.test_client()

    response = client.post(
        "/api/login",
        data=json.dumps({
            "username": "testuser",
            "password": "testpass"
        }),
        content_type="application/json"
    )

    assert response.status_code == 200