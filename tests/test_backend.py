"""
test_backend.py — Pruebas del backend API de Vault-Tec SecDevOps.
==================================================================
Niveles:
  1. Unitarias puras    — bcrypt, JWT, rate limiting (sin BD ni red)
  2. Integración HTTP   — endpoints completos con MySQL mockeado
  3. Seguridad HTTP     — cabeceras OWASP, control de acceso por rol
  4. Contrato API       — estructura de respuestas JSON

Ejecución:
  pytest tests/test_backend.py -v
  pytest tests/test_backend.py -v --cov=backend --cov-report=term-missing
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

os.environ["SECRET_KEY"]     = "vault-tec-test-secret-32bytes-xx"
os.environ["MYSQL_HOST"]     = "localhost"
os.environ["MYSQL_DATABASE"] = "vault_test"
os.environ["MYSQL_USER"]     = "vaultuser"
os.environ["MYSQL_PASSWORD"] = "vaultpass"

# Asegurar que el backend tiene prioridad en la resolución de 'import app'
_backend_path  = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
_frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
for p in [_backend_path, _frontend_path]:
    if p in sys.path:
        sys.path.remove(p)
sys.path.insert(0, _backend_path)


# ── Helpers ──────────────────────────────────────────────────────────────────

def mk_cur(one=None, all_=None, lastrowid=1):
    c = MagicMock()
    c.fetchone.return_value = one
    c.fetchall.return_value = all_ or []
    c.lastrowid = lastrowid
    return c

def mk_db(cursor=None):
    d = MagicMock()
    d.is_connected.return_value = True
    d.cursor.return_value = cursor if cursor is not None else mk_cur()
    return d

def setup_backend():
    import app as A
    A._pool = MagicMock()
    A.app.config["TESTING"] = True
    A._login_attempts.clear()
    return A

def admin_jwt(A):
    return A.create_token(1, "overseer", "admin")

def user_jwt(A):
    return A.create_token(2, "dweller", "user")

def bearer(token):
    return {"Authorization": f"Bearer {token}"}


# ════════════════════════════════════════════════════════════════════════════
# NIVEL 1 — UNITARIAS PURAS: bcrypt
# ════════════════════════════════════════════════════════════════════════════

class TestBcrypt:
    """Verifica que el hash de contraseñas cumple los requisitos de seguridad."""

    def test_hash_nunca_es_texto_plano(self):
        from app import hash_password
        h = hash_password("Overseer2077!")
        assert h != "Overseer2077!"
        assert len(h) > 30

    def test_hash_tiene_prefijo_bcrypt(self):
        """Los hashes bcrypt siempre empiezan con $2b$ (OWASP A02)."""
        from app import hash_password
        h = hash_password("cualquier_clave")
        assert h.startswith("$2b$") or h.startswith("$2a$")

    def test_verificacion_correcta(self):
        from app import hash_password, verify_password
        h = hash_password("Dweller2077!")
        assert verify_password("Dweller2077!", h) is True

    def test_verificacion_incorrecta(self):
        from app import hash_password, verify_password
        h = hash_password("Dweller2077!")
        assert verify_password("WrongPassword!", h) is False

    def test_salt_aleatorio_hashes_distintos(self):
        """Dos hashes del mismo password deben diferir (salt único por llamada)."""
        from app import hash_password
        h1 = hash_password("misma_clave")
        h2 = hash_password("misma_clave")
        assert h1 != h2

    def test_ambos_hashes_verifican(self):
        """Aunque los hashes difieran, ambos deben verificar correctamente."""
        from app import hash_password, verify_password
        h1 = hash_password("misma_clave")
        h2 = hash_password("misma_clave")
        assert verify_password("misma_clave", h1)
        assert verify_password("misma_clave", h2)

    def test_hash_no_contiene_password_en_claro(self):
        from app import hash_password
        h = hash_password("SecretPassword1!")
        assert "SecretPassword1!" not in h


# ════════════════════════════════════════════════════════════════════════════
# NIVEL 1 — UNITARIAS PURAS: JWT
# ════════════════════════════════════════════════════════════════════════════

class TestJWT:
    """Verifica la generación y verificación de tokens JWT."""

    def test_token_overseer_contiene_rol_admin(self):
        from app import create_token, verify_token
        token   = create_token(1, "overseer", "admin")
        payload = verify_token(token)
        assert payload["user"] == "overseer"
        assert payload["role"] == "admin"
        assert payload["sub"]  == "1"

    def test_token_dweller_contiene_rol_user(self):
        from app import create_token, verify_token
        token   = create_token(2, "dweller", "user")
        payload = verify_token(token)
        assert payload["role"] == "user"
        assert payload["user"] == "dweller"

    def test_token_invalido_lanza_excepcion(self):
        import jwt
        from app import verify_token
        with pytest.raises(jwt.InvalidTokenError):
            verify_token("vault.tec.token.falso")

    def test_token_manipulado_rechazado(self):
        """Modificar la firma debe invalidar el token (OWASP A02)."""
        import jwt
        from app import create_token, verify_token
        token  = create_token(1, "overseer", "admin")
        parts  = token.split(".")
        tampered = parts[0] + "." + parts[1] + ".firma_overseer_falsa"
        with pytest.raises(jwt.InvalidTokenError):
            verify_token(tampered)

    def test_token_contiene_expiracion(self):
        from app import create_token, verify_token
        token   = create_token(1, "overseer", "admin")
        payload = verify_token(token)
        assert "exp" in payload
        assert "iat" in payload


# ════════════════════════════════════════════════════════════════════════════
# NIVEL 1 — UNITARIAS PURAS: Rate limiting
# ════════════════════════════════════════════════════════════════════════════

class TestRateLimit:
    """Verifica protección contra fuerza bruta (OWASP A07)."""

    def setup_method(self):
        import app as A
        A._login_attempts.clear()

    def test_cinco_intentos_permitidos(self):
        from app import check_rate_limit
        for _ in range(10):
            assert check_rate_limit("10.0.0.1") is True

    def test_sexto_intento_bloqueado(self):
        from app import check_rate_limit
        ip = "10.0.0.2"
        for _ in range(10):
            check_rate_limit(ip)
        assert check_rate_limit(ip) is False

    def test_ips_distintas_son_independientes(self):
        from app import check_rate_limit
        for _ in range(10):
            check_rate_limit("192.168.1.1")
        # IP diferente no está bloqueada
        assert check_rate_limit("192.168.1.2") is True

    def test_bloqueo_no_afecta_a_otras_ips(self):
        from app import check_rate_limit
        for _ in range(11):
            check_rate_limit("1.2.3.4")
        assert check_rate_limit("5.6.7.8") is True


# ════════════════════════════════════════════════════════════════════════════
# NIVEL 2 — INTEGRACIÓN: /api/health
# ════════════════════════════════════════════════════════════════════════════

class TestHealth:
    def test_health_ok_con_db_disponible(self):
        A = setup_backend()
        cur = mk_cur(one=(1,))
        with patch("app.get_db", return_value=mk_db(cur)):
            with A.app.test_client() as c:
                r = c.get("/api/health")
        assert r.status_code == 200
        data = r.get_json()
        assert data["status"]   == "ok"
        assert data["database"] == "ok"
        assert data["engine"]   == "MySQL 8"

    def test_health_devuelve_503_si_db_falla(self):
        A = setup_backend()
        import mysql.connector
        with patch("app.get_db", side_effect=mysql.connector.Error("conn error")):
            with A.app.test_client() as c:
                r = c.get("/api/health")
        assert r.status_code == 503


# ════════════════════════════════════════════════════════════════════════════
# NIVEL 2 — INTEGRACIÓN: /api/login
# ════════════════════════════════════════════════════════════════════════════

class TestLogin:
    def test_login_overseer_correcto(self):
        import bcrypt as _b
        A = setup_backend()
        h = _b.hashpw(b"Overseer2077!", _b.gensalt()).decode()
        cur = mk_cur(one={"id": 1, "username": "overseer",
                          "password_hash": h, "role": "admin", "active": 1})
        with patch("app.get_db",         return_value=mk_db(cur)), \
             patch("app.check_rate_limit", return_value=True), \
             patch("app.log_action"):
            with A.app.test_client() as c:
                r = c.post("/api/login",
                           json={"username": "overseer", "password": "Overseer2077!"},
                           content_type="application/json")
        assert r.status_code == 200
        data = r.get_json()
        assert "token" in data
        assert data["role"]     == "admin"
        assert data["username"] == "overseer"

    def test_login_dweller_correcto(self):
        import bcrypt as _b
        A = setup_backend()
        h = _b.hashpw(b"Dweller2077!", _b.gensalt()).decode()
        cur = mk_cur(one={"id": 2, "username": "dweller",
                          "password_hash": h, "role": "user", "active": 1})
        with patch("app.get_db",         return_value=mk_db(cur)), \
             patch("app.check_rate_limit", return_value=True), \
             patch("app.log_action"):
            with A.app.test_client() as c:
                r = c.post("/api/login",
                           json={"username": "dweller", "password": "Dweller2077!"},
                           content_type="application/json")
        assert r.status_code == 200
        assert r.get_json()["role"] == "user"

    def test_login_password_incorrecto_devuelve_401(self):
        import bcrypt as _b
        A = setup_backend()
        h = _b.hashpw(b"Overseer2077!", _b.gensalt()).decode()
        cur = mk_cur(one={"id": 1, "username": "overseer",
                          "password_hash": h, "role": "admin", "active": 1})
        with patch("app.get_db",         return_value=mk_db(cur)), \
             patch("app.check_rate_limit", return_value=True), \
             patch("app.log_action"):
            with A.app.test_client() as c:
                r = c.post("/api/login",
                           json={"username": "overseer", "password": "WRONG"},
                           content_type="application/json")
        assert r.status_code == 401

    def test_login_usuario_inexistente_devuelve_401(self):
        """A07 — mismo código que password incorrecto (sin user oracle)."""
        A = setup_backend()
        cur = mk_cur(one=None)
        with patch("app.get_db",         return_value=mk_db(cur)), \
             patch("app.check_rate_limit", return_value=True), \
             patch("app.log_action"):
            with A.app.test_client() as c:
                r = c.post("/api/login",
                           json={"username": "ghost", "password": "x"},
                           content_type="application/json")
        assert r.status_code == 401

    def test_login_rate_limit_devuelve_429(self):
        """A07 — rate limiting activo tras superar el umbral."""
        A = setup_backend()
        with patch("app.get_db",         return_value=mk_db()), \
             patch("app.check_rate_limit", return_value=False), \
             patch("app.log_action"):
            with A.app.test_client() as c:
                r = c.post("/api/login",
                           json={"username": "x", "password": "y"},
                           content_type="application/json")
        assert r.status_code == 429

    def test_login_body_vacio_devuelve_400(self):
        """A08 — validación de input: campos requeridos."""
        A = setup_backend()
        with patch("app.get_db",         return_value=mk_db()), \
             patch("app.check_rate_limit", return_value=True):
            with A.app.test_client() as c:
                r = c.post("/api/login", json={},
                           content_type="application/json")
        assert r.status_code == 400

    def test_login_cuenta_inactiva_devuelve_403(self):
        import bcrypt as _b
        A = setup_backend()
        h = _b.hashpw(b"Dweller2077!", _b.gensalt()).decode()
        cur = mk_cur(one={"id": 3, "username": "dweller",
                          "password_hash": h, "role": "user", "active": 0})
        with patch("app.get_db",         return_value=mk_db(cur)), \
             patch("app.check_rate_limit", return_value=True), \
             patch("app.log_action"):
            with A.app.test_client() as c:
                r = c.post("/api/login",
                           json={"username": "dweller", "password": "Dweller2077!"},
                           content_type="application/json")
        assert r.status_code == 403


# ════════════════════════════════════════════════════════════════════════════
# NIVEL 2 — INTEGRACIÓN: /api/profile
# ════════════════════════════════════════════════════════════════════════════

class TestProfile:
    def test_profile_sin_token_devuelve_401(self):
        A = setup_backend()
        with patch("app.get_db", return_value=mk_db()):
            with A.app.test_client() as c:
                r = c.get("/api/profile")
        assert r.status_code == 401

    def test_profile_con_token_overseer(self):
        A = setup_backend()
        cur = mk_cur(one={"id": 1, "username": "overseer",
                          "role": "admin", "created_at": "2077-01-01"})
        with patch("app.get_db", return_value=mk_db(cur)):
            with A.app.test_client() as c:
                r = c.get("/api/profile",
                          headers=bearer(admin_jwt(A)))
        assert r.status_code == 200
        data = r.get_json()
        assert data["username"] == "overseer"
        assert data["role"]     == "admin"

    def test_profile_no_expone_password_hash(self):
        """A08 — la respuesta de perfil nunca debe incluir el hash."""
        A = setup_backend()
        cur = mk_cur(one={"id": 1, "username": "overseer",
                          "role": "admin", "created_at": "2077-01-01"})
        with patch("app.get_db", return_value=mk_db(cur)):
            with A.app.test_client() as c:
                r = c.get("/api/profile", headers=bearer(admin_jwt(A)))
        assert "password" not in r.get_json()
        assert "password_hash" not in r.get_json()


# ════════════════════════════════════════════════════════════════════════════
# NIVEL 2 — INTEGRACIÓN: /api/projects
# ════════════════════════════════════════════════════════════════════════════

class TestProjects:
    def test_listar_directivas_con_token(self):
        A = setup_backend()
        cur = mk_cur(all_=[
            {"id": 1, "name": "Proyecto Overseer Alpha",
             "description": "Test", "status": "activo",
             "owner": "overseer", "created_at": "2077-01-01"}
        ])
        with patch("app.get_db",    return_value=mk_db(cur)), \
             patch("app.log_action"):
            with A.app.test_client() as c:
                r = c.get("/api/projects", headers=bearer(user_jwt(A)))
        assert r.status_code == 200
        data = r.get_json()
        assert "projects" in data
        assert len(data["projects"]) == 1

    def test_listar_directivas_sin_token_devuelve_401(self):
        A = setup_backend()
        with patch("app.get_db", return_value=mk_db()):
            with A.app.test_client() as c:
                r = c.get("/api/projects")
        assert r.status_code == 401

    def test_crear_directiva_admin_ok(self):
        A = setup_backend()
        cur = mk_cur(lastrowid=10)
        with patch("app.get_db",    return_value=mk_db(cur)), \
             patch("app.log_action"):
            with A.app.test_client() as c:
                r = c.post("/api/projects",
                           json={"name": "Directiva Omega",
                                 "description": "Prueba",
                                 "status": "activo"},
                           headers=bearer(admin_jwt(A)),
                           content_type="application/json")
        assert r.status_code == 201
        assert r.get_json()["id"] == 10

    def test_crear_directiva_sin_nombre_devuelve_400(self):
        A = setup_backend()
        with patch("app.get_db",    return_value=mk_db()), \
             patch("app.log_action"):
            with A.app.test_client() as c:
                r = c.post("/api/projects",
                           json={"description": "Sin nombre"},
                           headers=bearer(admin_jwt(A)),
                           content_type="application/json")
        assert r.status_code == 400

    def test_crear_directiva_usuario_normal_devuelve_403(self):
        """A01 — solo overseer puede crear directivas."""
        A = setup_backend()
        with patch("app.get_db",    return_value=mk_db()), \
             patch("app.log_action"):
            with A.app.test_client() as c:
                r = c.post("/api/projects",
                           json={"name": "Hack"},
                           headers=bearer(user_jwt(A)),
                           content_type="application/json")
        assert r.status_code == 403

    def test_crear_directiva_estado_invalido_devuelve_400(self):
        A = setup_backend()
        with patch("app.get_db",    return_value=mk_db()), \
             patch("app.log_action"):
            with A.app.test_client() as c:
                r = c.post("/api/projects",
                           json={"name": "Test", "status": "estado_invalido"},
                           headers=bearer(admin_jwt(A)),
                           content_type="application/json")
        assert r.status_code == 400


# ════════════════════════════════════════════════════════════════════════════
# NIVEL 3 — INTEGRACIÓN: endpoints de administración
# ════════════════════════════════════════════════════════════════════════════

class TestAdminEndpoints:
    def test_listar_residentes_sin_token_devuelve_401(self):
        A = setup_backend()
        with patch("app.get_db", return_value=mk_db()):
            with A.app.test_client() as c:
                r = c.get("/api/admin/users")
        assert r.status_code == 401

    def test_listar_residentes_dweller_devuelve_403(self):
        """A01 — dweller no puede acceder a la lista de residentes."""
        A = setup_backend()
        with patch("app.get_db", return_value=mk_db()):
            with A.app.test_client() as c:
                r = c.get("/api/admin/users",
                          headers=bearer(user_jwt(A)))
        assert r.status_code == 403

    def test_listar_residentes_overseer_ok(self):
        A = setup_backend()
        cur = mk_cur(all_=[
            {"id": 1, "username": "overseer", "role": "admin",
             "active": 1, "created_at": "2077-01-01"},
            {"id": 2, "username": "dweller",  "role": "user",
             "active": 1, "created_at": "2077-01-02"},
        ])
        with patch("app.get_db",    return_value=mk_db(cur)), \
             patch("app.log_action"):
            with A.app.test_client() as c:
                r = c.get("/api/admin/users",
                          headers=bearer(admin_jwt(A)))
        assert r.status_code == 200
        data = r.get_json()
        assert len(data["users"]) == 2
        # Ningún usuario debe exponer su password_hash (A08)
        for u in data["users"]:
            assert "password_hash" not in u
            assert "password"      not in u

    def test_logs_overseer_ok(self):
        A = setup_backend()
        cur = mk_cur(all_=[
            {"id": 1, "username": "overseer", "action": "login_success",
             "ip": "127.0.0.1", "detail": "", "created_at": "2077-01-01"},
        ])
        with patch("app.get_db", return_value=mk_db(cur)):
            with A.app.test_client() as c:
                r = c.get("/api/admin/logs",
                          headers=bearer(admin_jwt(A)))
        assert r.status_code == 200
        assert "logs" in r.get_json()

    def test_logs_dweller_devuelve_403(self):
        A = setup_backend()
        with patch("app.get_db", return_value=mk_db()):
            with A.app.test_client() as c:
                r = c.get("/api/admin/logs",
                          headers=bearer(user_jwt(A)))
        assert r.status_code == 403

    def test_stats_overseer_ok(self):
        A = setup_backend()
        cur = MagicMock()
        cur.fetchone.side_effect = [
            {"total": 2}, {"total": 1}, {"total": 5},
            {"total": 12}, {"total": 0}
        ]
        cur.fetchall.return_value = [{"status": "activo", "total": 3}]
        with patch("app.get_db", return_value=mk_db(cur)):
            with A.app.test_client() as c:
                r = c.get("/api/admin/stats",
                          headers=bearer(admin_jwt(A)))
        assert r.status_code == 200
        data = r.get_json()
        assert "users"    in data
        assert "projects" in data

    def test_toggle_residente_overseer_ok(self):
        A = setup_backend()
        cur = mk_cur(one={"id": 2, "username": "dweller", "active": 1})
        with patch("app.get_db",    return_value=mk_db(cur)), \
             patch("app.log_action"):
            with A.app.test_client() as c:
                r = c.post("/api/admin/users/2/toggle",
                           headers=bearer(admin_jwt(A)))
        assert r.status_code == 200

    def test_toggle_residente_inexistente_devuelve_404(self):
        A = setup_backend()
        cur = mk_cur(one=None)
        with patch("app.get_db",    return_value=mk_db(cur)), \
             patch("app.log_action"):
            with A.app.test_client() as c:
                r = c.post("/api/admin/users/999/toggle",
                           headers=bearer(admin_jwt(A)))
        assert r.status_code == 404


# ════════════════════════════════════════════════════════════════════════════
# NIVEL 4 — SEGURIDAD: cabeceras HTTP (OWASP A05)
# ════════════════════════════════════════════════════════════════════════════

class TestSecurityHeaders:
    def test_cabeceras_owasp_presentes(self):
        A = setup_backend()
        cur = mk_cur(one=(1,))
        with patch("app.get_db", return_value=mk_db(cur)):
            with A.app.test_client() as c:
                r = c.get("/api/health")
        assert r.headers.get("X-Frame-Options")        == "DENY"
        assert r.headers.get("X-Content-Type-Options") == "nosniff"
        assert r.headers.get("X-XSS-Protection")       == "1; mode=block"
        assert r.headers.get("Cache-Control")          == "no-store"
        csp = r.headers.get("Content-Security-Policy", "")
        assert "default-src" in csp

    def test_ruta_inexistente_devuelve_404_json(self):
        A = setup_backend()
        with patch("app.get_db", return_value=mk_db()):
            with A.app.test_client() as c:
                r = c.get("/api/ruta_que_no_existe")
        assert r.status_code == 404

    def test_token_jwt_expirado_devuelve_401(self):
        """A07 — tokens expirados deben ser rechazados."""
        import jwt as _jwt
        from datetime import datetime, timedelta
        A = setup_backend()
        expired_payload = {
            "sub": "1", "user": "overseer", "role": "admin",
            "iat": datetime.utcnow() - timedelta(hours=3),
            "exp": datetime.utcnow() - timedelta(hours=2),
        }
        expired_token = _jwt.encode(
            expired_payload, A.SECRET_KEY, algorithm="HS256"
        )
        with patch("app.get_db", return_value=mk_db()):
            with A.app.test_client() as c:
                r = c.get("/api/profile",
                          headers=bearer(expired_token))
        assert r.status_code == 401
