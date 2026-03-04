# 🏚️ Fallout SecDevOps — Vault 33

> Práctica de Puesta en Producción Segura — CEU San Pablo  
> Aplicación web full-stack con temática Fallout, desarrollada siguiendo principios de seguridad, contenedores y CI/CD.

---

## 📋 Índice

- [Arquitectura](#arquitectura)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Entorno de desarrollo](#entorno-de-desarrollo)
- [Cómo ejecutar el proyecto](#cómo-ejecutar-el-proyecto)
- [Autenticación y roles](#autenticación-y-roles)
- [Tests](#tests)
- [CI/CD con GitHub Actions](#cicd-con-github-actions)
- [Seguridad OWASP](#seguridad-owasp)

---

## 🏗️ Arquitectura

El proyecto está dividido en tres servicios que se comunican entre sí mediante Docker:
```
[Navegador] → [Frontend Flask :5000] → [Backend API Flask :5001] → [MySQL :3306]
```

| Servicio | Tecnología | Puerto | Descripción |
|---|---|---|---|
| Frontend | Python Flask | 5000 | Interfaz web, gestión de sesiones |
| Backend | Python Flask API | 5001 | API REST, lógica de negocio |
| Base de datos | MySQL 8 | 3306 | Persistencia de usuarios y vault |

---

## 📁 Estructura del proyecto
```
fallout-secdevops/
├── .github/
│   └── workflows/
│       └── ci.yml              # Pipeline de CI con GitHub Actions
├── backend/
│   ├── app.py                  # API REST: /api/status, /api/vault, /api/login, /api/register
│   ├── auth_service.py         # Lógica de autenticación (hash, verificación)
│   ├── requirements.txt        # Dependencias del backend
│   ├── Dockerfile              # Imagen Docker del backend
│   └── tests/
│       ├── test_unit.py        # Tests unitarios (sin base de datos)
│       ├── test_backend.py     # Tests de integración (con base de datos)
│       └── test_auth.py        # Tests de autenticación
├── frontend/
│   ├── app.py                  # Servidor Flask frontend, gestión de sesión y roles
│   ├── requirements.txt        # Dependencias del frontend
│   ├── Dockerfile              # Imagen Docker del frontend
│   └── templates/
│       ├── login.html          # Formulario de acceso al vault
│       └── dashboard.html      # Panel principal (diferenciado por rol)
├── docs/
│   └── venv-prompt.png         # Captura del entorno virtual activo
├── docker-compose.yml          # Orquestación de los tres servicios
├── .gitignore                  # Excluye venv, .env, __pycache__
├── OWASP.md                    # Análisis de seguridad OWASP Web + API
└── README.md
```

---

## 💻 Entorno de desarrollo

Se ha utilizado un **entorno virtual de Python (venv)** para aislar las dependencias del proyecto de otros entornos del sistema.
```bash
# Crear el entorno virtual
python -m venv venv

# Activar en Windows
venv\Scripts\activate

# Activar en Linux/Mac
source venv/bin/activate
```

Captura del prompt con el entorno virtual activo:

![Entorno virtual activo](./docs/venv-prompt.png)

---

## 🚀 Cómo ejecutar el proyecto

### Requisitos
- Docker Desktop instalado
- Git

### Pasos
```bash
# 1. Clonar el repositorio
git clone https://github.com/Jose-CEU/fallout-secdevops.git
cd fallout-secdevops

# 2. Levantar todos los servicios
docker-compose up --build

# 3. Acceder a la aplicación
http://localhost:5000
```

Los tres contenedores se levantarán automáticamente: `vault_db`, `vault_backend` y `vault_frontend`.

---

## 🔐 Autenticación y roles

El sistema tiene dos tipos de usuario con comportamiento visual diferenciado.  
La autenticación se gestiona en `frontend/app.py` mediante sesiones Flask con `SECRET_KEY` cargada desde variable de entorno.

| Usuario | Contraseña | Rol | Fondo | Título |
|---|---|---|---|---|
| `overseer` | `overseer_admin_2024` | Admin | Azul oscuro `#003366` | Vault Control Panel - Overseer |
| `dweller` | `dweller_user_2024` | User | Verde oscuro `#003300` | Vault Terminal - Dweller |

La diferenciación visual está implementada en `frontend/templates/dashboard.html`:
```html
{% if role == "admin" %}
<body style="background-color:#003366; color:white;">
{% else %}
<body style="background-color:#003300; color:white;">
{% endif %}
```

---

## 🧪 Tests

Los tests están en `backend/tests/` y se ejecutan automáticamente en el pipeline de CI.

### Tests unitarios (`test_unit.py`)
No requieren base de datos. Comprueban funciones individuales:

| Test | Descripción |
|---|---|
| `test_status_code` | `/api/status` devuelve HTTP 200 |
| `test_status_json` | Respuesta JSON contiene `status: ok` y `version: 1.0.0` |
| `test_login_missing_fields` | Login sin campos devuelve HTTP 400 |
| `test_register_short_password` | Contraseña corta devuelve HTTP 400 |

### Tests de integración (`test_backend.py`, `test_auth.py`)
Requieren base de datos MySQL activa. Comprueban la comunicación entre componentes:

| Test | Descripción |
|---|---|
| `test_api_status` | La API responde correctamente |
| `test_register_and_login` | Registro de usuario y login exitoso |
| `test_login_wrong_password` | Credenciales incorrectas devuelven HTTP 401 |
| `test_register` | Registro devuelve HTTP 201 |
| `test_login` | Login correcto devuelve HTTP 200 |

### Ejecutar tests manualmente
```bash
cd backend
pytest
```

---

## ⚙️ CI/CD con GitHub Actions

Definido en `.github/workflows/ci.yml`.  
Se ejecuta automáticamente en cada **push** y **pull request** a `main`.

El pipeline:
1. Levanta un servicio MySQL en el runner
2. Instala las dependencias de `backend/requirements.txt`
3. Ejecuta todos los tests con `pytest`
```yaml
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
```

---

## 🔒 Seguridad OWASP

Se han revisado y aplicado medidas del **OWASP Top Ten de aplicaciones web** y del **OWASP API Security Top Ten**.

Ver análisis completo en [OWASP.md](./OWASP.md).

Resumen de medidas aplicadas:

| OWASP | Medida | Dónde |
|---|---|---|
| A02 Cryptographic Failures | Contraseñas hasheadas con bcrypt | `backend/auth_service.py` |
| A02 Cryptographic Failures | SECRET_KEY desde variable de entorno | `frontend/app.py`, `docker-compose.yml` |
| A03 Injection | Queries parametrizadas con `%s` | `backend/app.py` |
| A07 Auth Failures | Validación mínimo 6 caracteres | `backend/app.py` |
| A07 Auth Failures | Logout limpia sesión completa | `frontend/app.py` |
| A01 Broken Access Control | Rutas protegidas redirigen a login | `frontend/app.py` |

---

## 🌿 Gestión de ramas

El proyecto sigue un flujo de trabajo con ramas de features y pull requests:

| Rama | Descripción |
|---|---|
| `main` | Rama principal estable |
| `fix/vault-endpoint` | Fix del endpoint incorrecto en frontend |
| `feature/readme` | Documentación inicial |
| `feature/frontend-docker` | Dockerfile frontend y docker-compose completo |
| `feature/owasp-docs` | Documentación OWASP |
| `feature/tests` | Mejora y separación de tests |

| `feature/readme-pro` | README profesional |
