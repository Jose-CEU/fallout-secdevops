# Tests de INTEGRACIÓN - requieren base de datos real
import pytest
from app import app

def test_api_status():
    """Integración: verifica que la API responde correctamente"""
    client = app.test_client()
    response = client.get("/api/status")
    assert response.status_code == 200

def test_register_and_login():
    """Integración: registra un usuario y luego hace login"""
    client = app.test_client()

    # Registro
    response = client.post("/api/register",
        json={"username": "vaultdweller", "password": "secure123"},
        content_type="application/json"
    )
    assert response.status_code in [201, 409]

    # Login
    response = client.post("/api/login",
        json={"username": "vaultdweller", "password": "secure123"},
        content_type="application/json"
    )
    assert response.status_code == 200

def test_login_wrong_password():
    """Integración: login con contraseña incorrecta devuelve 401"""
    client = app.test_client()
    response = client.post("/api/login",
        json={"username": "vaultdweller", "password": "wrongpass"},
        content_type="application/json"
    )
    assert response.status_code == 401