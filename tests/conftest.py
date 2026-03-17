"""
conftest.py — Configuración global de pytest para Vault-Tec SecDevOps.

Establece el path de Python para que 'import app' resuelva al backend,
inyecta variables de entorno para tests y expone fixtures compartidos.
"""

import os
import sys

# ── Path setup ──────────────────────────────────────────────────────────────
ROOT          = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_PATH  = os.path.join(ROOT, "backend")
FRONTEND_PATH = os.path.join(ROOT, "frontend")

# Añadir ambos paths sin duplicados — cada test file gestiona su propio import
for p in [BACKEND_PATH, FRONTEND_PATH]:
    if p not in sys.path:
        sys.path.append(p)

# ── Variables de entorno para tests ─────────────────────────────────────────
for key, val in {
    "SECRET_KEY":      "vault-tec-test-secret-32bytes-xx",
    "FLASK_SECRET_KEY": "vault-tec-test-secret-32bytes-xx",
    "BACKEND_URL":     "http://backend:5001",
    "MYSQL_HOST":      "localhost",
    "MYSQL_DATABASE":  "vault_test",
    "MYSQL_USER":      "vaultuser",
    "MYSQL_PASSWORD":  "vaultpass",
}.items():
    os.environ.setdefault(key, val)
