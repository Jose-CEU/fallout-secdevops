import json
import pytest
from app import app, get_db_connection
from werkzeug.security import generate_password_hash

@pytest.fixture(autouse=True)
def setup_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'user'
            )
        """)
        cursor.execute("SELECT * FROM users WHERE username = %s", ("overseer",))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                ("overseer", generate_password_hash("overseer_admin_2024"), "admin")
            )
        conn.commit()
        cursor.close()
        conn.close()

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