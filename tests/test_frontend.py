"""
test_frontend.py — Pruebas del frontend de Vault-Tec SecDevOps.
===============================================================
Cubre rutas Flask del frontend con el backend mockeado via `responses`.

Ejecución:
  pytest tests/test_frontend.py -v
"""

import os
import sys
import pytest
import responses as resp_lib

os.environ["FLASK_SECRET_KEY"] = "vault-tec-test-frontend-secret"
os.environ["SECRET_KEY"]       = "vault-tec-test-frontend-secret"
os.environ["BACKEND_URL"]      = "http://backend:5001"

# Asegurar que el frontend tiene prioridad en la resolución de 'import app'
_frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
_frontend_path = os.path.abspath(_frontend_path)
_backend_path  = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))

# Retirar backend del frente del path para que el frontend gane
for p in [_backend_path, _frontend_path]:
    if p in sys.path:
        sys.path.remove(p)
sys.path.insert(0, _frontend_path)

from app import app as flask_app

FAKE_TOKEN = "eyJhbGciOiJIUzI1NiJ9.vault.tec.token"
BACKEND    = "http://backend:5001"


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


def _session_overseer(client):
    with client.session_transaction() as s:
        s["token"]    = FAKE_TOKEN
        s["username"] = "overseer"
        s["role"]     = "admin"

def _session_dweller(client):
    with client.session_transaction() as s:
        s["token"]    = FAKE_TOKEN
        s["username"] = "dweller"
        s["role"]     = "user"


# ════════════════════════════════════════════════════════════════════════════
# RUTAS — Redirecciones sin sesión
# ════════════════════════════════════════════════════════════════════════════

class TestRutasPublicas:
    def test_raiz_redirige_a_login(self, client):
        r = client.get("/")
        assert r.status_code == 302
        assert "/login" in r.headers["Location"]

    def test_login_get_devuelve_200(self, client):
        r = client.get("/login")
        assert r.status_code == 200

    def test_login_muestra_terminal_vault_tec(self, client):
        r = client.get("/login")
        assert b"VAULT-TEC" in r.data

    def test_login_muestra_credenciales_demo(self, client):
        r = client.get("/login")
        assert b"overseer" in r.data
        assert b"dweller"  in r.data

    def test_dashboard_sin_sesion_redirige(self, client):
        r = client.get("/dashboard")
        assert r.status_code == 302

    def test_admin_sin_sesion_redirige(self, client):
        r = client.get("/admin")
        assert r.status_code == 302

    def test_new_project_sin_sesion_redirige(self, client):
        r = client.get("/admin/new-project")
        assert r.status_code == 302

    def test_login_campos_vacios_muestra_error(self, client):
        r = client.post("/login", data={"username": "", "password": ""})
        assert r.status_code == 200
        assert b"campos" in r.data or b"completa" in r.data


# ════════════════════════════════════════════════════════════════════════════
# LOGIN — flujo completo con backend mockeado
# ════════════════════════════════════════════════════════════════════════════

class TestLoginFlujo:
    @resp_lib.activate
    def test_login_overseer_redirige_a_dashboard(self, client):
        resp_lib.add(
            resp_lib.POST, f"{BACKEND}/api/login",
            json={"token": FAKE_TOKEN, "username": "overseer",
                  "role": "admin", "message": "ok"},
            status=200
        )
        r = client.post("/login",
                        data={"username": "overseer",
                              "password": "Overseer2077!"})
        assert r.status_code == 302
        assert "dashboard" in r.headers["Location"]

    @resp_lib.activate
    def test_login_dweller_redirige_a_dashboard(self, client):
        resp_lib.add(
            resp_lib.POST, f"{BACKEND}/api/login",
            json={"token": FAKE_TOKEN, "username": "dweller",
                  "role": "user", "message": "ok"},
            status=200
        )
        r = client.post("/login",
                        data={"username": "dweller",
                              "password": "Dweller2077!"})
        assert r.status_code == 302

    @resp_lib.activate
    def test_login_credenciales_incorrectas_muestra_error(self, client):
        resp_lib.add(
            resp_lib.POST, f"{BACKEND}/api/login",
            json={"error": "Credenciales incorrectas"},
            status=401
        )
        r = client.post("/login",
                        data={"username": "overseer",
                              "password": "WRONG"})
        assert r.status_code == 200
        assert b"Credenciales" in r.data or b"incorrectas" in r.data

    @resp_lib.activate
    def test_login_rate_limit_muestra_aviso(self, client):
        resp_lib.add(
            resp_lib.POST, f"{BACKEND}/api/login",
            json={"error": "Demasiados intentos. Espera 15 minutos."},
            status=429
        )
        r = client.post("/login",
                        data={"username": "x", "password": "y"})
        assert r.status_code == 200
        assert b"intentos" in r.data or b"Espera" in r.data

    def test_login_con_sesion_activa_redirige_a_dashboard(self, client):
        _session_overseer(client)
        r = client.get("/login")
        assert r.status_code == 302
        assert "dashboard" in r.headers["Location"]

    def test_logout_limpia_sesion(self, client):
        _session_overseer(client)
        r = client.get("/logout")
        assert r.status_code == 302
        # Después de logout, /dashboard debe redirigir a login
        r2 = client.get("/dashboard")
        assert r2.status_code == 302


# ════════════════════════════════════════════════════════════════════════════
# DASHBOARD — diferenciación por rol
# ════════════════════════════════════════════════════════════════════════════

class TestDashboard:
    @resp_lib.activate
    def test_dashboard_overseer_muestra_estadisticas(self, client):
        _session_overseer(client)
        resp_lib.add(resp_lib.GET, f"{BACKEND}/api/projects",
                     json={"projects": [], "total": 0}, status=200)
        resp_lib.add(resp_lib.GET, f"{BACKEND}/api/admin/stats",
                     json={"users": 2, "projects": 3,
                           "audit_log_entries": 10,
                           "failed_logins_1h": 0,
                           "projects_by_status": {}},
                     status=200)
        r = client.get("/dashboard")
        assert r.status_code == 200
        assert b"OVERSEER" in r.data or b"overseer" in r.data.lower()

    @resp_lib.activate
    def test_dashboard_dweller_no_muestra_panel_admin(self, client):
        _session_dweller(client)
        resp_lib.add(resp_lib.GET, f"{BACKEND}/api/projects",
                     json={"projects": [], "total": 0}, status=200)
        r = client.get("/dashboard")
        assert r.status_code == 200
        # El dweller no debe ver botones de administración
        assert b"Gestionar residentes" not in r.data

    @resp_lib.activate
    def test_dashboard_muestra_directivas(self, client):
        _session_dweller(client)
        resp_lib.add(resp_lib.GET, f"{BACKEND}/api/projects",
                     json={"projects": [
                         {"id": 1, "name": "Proyecto Overseer Alpha",
                          "description": "Test", "status": "activo",
                          "owner": "overseer", "created_at": "2077-01-01"}
                     ], "total": 1}, status=200)
        r = client.get("/dashboard")
        assert r.status_code == 200
        assert b"Overseer Alpha" in r.data

    def test_dashboard_token_expirado_redirige_a_login(self, client):
        from unittest.mock import patch, MagicMock
        _session_overseer(client)
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.ok = False
        with patch("app.call_backend", return_value=mock_resp):
            r = client.get("/dashboard")
        assert r.status_code == 302
        assert "/login" in r.headers["Location"]


# ════════════════════════════════════════════════════════════════════════════
# PANEL ADMIN — control de acceso por rol
# ════════════════════════════════════════════════════════════════════════════

class TestAdminPanel:
    @resp_lib.activate
    def test_admin_overseer_puede_acceder(self, client):
        _session_overseer(client)
        resp_lib.add(resp_lib.GET, f"{BACKEND}/api/admin/users",
                     json={"users": [], "total": 0}, status=200)
        resp_lib.add(resp_lib.GET, f"{BACKEND}/api/admin/logs",
                     json={"logs": [], "total": 0}, status=200)
        resp_lib.add(resp_lib.GET, f"{BACKEND}/api/admin/stats",
                     json={"users": 2, "projects": 3,
                           "audit_log_entries": 0,
                           "failed_logins_1h": 0,
                           "projects_by_status": {}},
                     status=200)
        r = client.get("/admin")
        assert r.status_code == 200

    def test_admin_dweller_redirigido(self, client):
        """A01 — dweller no puede acceder al panel de administración."""
        _session_dweller(client)
        r = client.get("/admin")
        assert r.status_code == 302

    @resp_lib.activate
    def test_nueva_directiva_overseer_ok(self, client):
        _session_overseer(client)
        resp_lib.add(resp_lib.POST, f"{BACKEND}/api/projects",
                     json={"message": "Proyecto creado", "id": 7},
                     status=201)
        r = client.post("/admin/new-project",
                        data={"name": "Directiva Omega",
                              "description": "Test",
                              "status": "activo"})
        assert r.status_code == 302   # redirige al dashboard tras crear

    def test_nueva_directiva_dweller_redirigido(self, client):
        """A01 — dweller no puede crear directivas."""
        _session_dweller(client)
        r = client.post("/admin/new-project",
                        data={"name": "Hack"})
        assert r.status_code == 302


# ════════════════════════════════════════════════════════════════════════════
# PROXY API — acceso directo a endpoints para Postman
# ════════════════════════════════════════════════════════════════════════════

class TestProxyAPI:
    @resp_lib.activate
    def test_proxy_health(self, client):
        resp_lib.add(resp_lib.GET, f"{BACKEND}/api/health",
                     json={"status": "ok", "database": "ok",
                           "engine": "MySQL 8"},
                     status=200)
        r = client.get("/api/health")
        assert r.status_code == 200
        assert b"ok" in r.data

    @resp_lib.activate
    def test_proxy_login(self, client):
        resp_lib.add(resp_lib.POST, f"{BACKEND}/api/login",
                     json={"token": FAKE_TOKEN, "username": "overseer",
                           "role": "admin"},
                     status=200)
        r = client.post("/api/login",
                        json={"username": "overseer",
                              "password": "Overseer2077!"},
                        content_type="application/json")
        assert r.status_code == 200

    @resp_lib.activate
    def test_proxy_backend_no_disponible(self, client):
        # No registramos ningún mock → ConnectionError
        r = client.get("/api/health")
        assert r.status_code == 503
