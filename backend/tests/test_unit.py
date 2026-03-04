# Tests UNITARIOS - no requieren base de datos
from unittest.mock import patch, MagicMock
from app import app

def test_status_code():
    """Verifica que el endpoint /api/status devuelve 200"""
    client = app.test_client()
    response = client.get("/api/status")
    assert response.status_code == 200

def test_status_json():
    """Verifica el contenido JSON de /api/status"""
    client = app.test_client()
    response = client.get("/api/status")
    assert response.json["status"] == "ok"
    assert response.json["version"] == "1.0.0"

def test_login_missing_fields():
    """Verifica que login sin campos devuelve 400"""
    client = app.test_client()
    response = client.post("/api/login",
        json={},
        content_type="application/json"
    )
    assert response.status_code == 400

def test_register_short_password():
    """Verifica que contraseña corta devuelve 400"""
    client = app.test_client()
    response = client.post("/api/register",
        json={"username": "test", "password": "123"},
        content_type="application/json"
    )
    assert response.status_code == 400