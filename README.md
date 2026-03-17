# ☢️ Vault-Tec SecDevOps — Vault 33

<div align="center">

[![CI/CD Pipeline](https://github.com/TU_USUARIO/vault-tec-secdevops/actions/workflows/ci.yml/badge.svg)](https://github.com/TU_USUARIO/vault-tec-secdevops/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3120/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MySQL 8](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)](https://dev.mysql.com/doc/relnotes/mysql/8.0/en/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![JWT](https://img.shields.io/badge/Pip--Boy-JWT%20Auth-4caf50)](https://jwt.io/)
[![bcrypt](https://img.shields.io/badge/Hashing-bcrypt%20rounds%3D12-brightgreen)](https://pypi.org/project/bcrypt/)
[![OWASP](https://img.shields.io/badge/OWASP-Top%2010-orange?logo=owasp&logoColor=white)](./OWASP.md)
[![Tests](https://img.shields.io/badge/Tests-70%20passing-success?logo=pytest)](./TESTS.md)
[![War](https://img.shields.io/badge/War-Never%20Changes-black)](https://fallout.fandom.com/wiki/Fallout)

```
 __   ___   _   _   _ _   _____     _____ ___ ___
 \ \ / / | | | | | | | | |_   _|   |_   _| __/ __|
  \ V /| |_| |_| |_| | |__ | |  _    | | | _| (__
   \_/ |____\___/\___/|____|_| (_)   |_| |___\___|

         ██████████████████████████████
         █  VAULT-TEC CORPORATION     █
         █  SECURITY PROTOCOL 7-ALPHA █
         █  AUTHORIZED PERSONNEL ONLY █
         ██████████████████████████████
              "Preparing for the Future"
```

**Aplicación web de seguridad para la asignatura SecDevOps — CEU San Pablo**

Gestor de directivas internas del Vault con autenticación JWT, roles diferenciados,
base de datos MySQL persistente y pipeline CI/CD completo en GitHub Actions.

> *"War. War never changes. But your authentication layer should."*

[☢️ Arquitectura](#️-arquitectura) · [🔧 Arranque](#-arranque-rápido) · [👤 Residentes](#-residentes-del-vault) · [📡 API](#-api--terminales-del-vault) · [📮 Postman](#-pruebas-con-postman) · [🧪 Tests](#-tests) · [⚙️ CI/CD](#️-cicd--github-actions) · [🛡️ OWASP](#️-seguridad-owasp)

</div>

---

## 📟 Índice

- [☢️ Arquitectura](#️-arquitectura)
- [🔧 Entorno de desarrollo](#-entorno-de-desarrollo)
- [🔧 Arranque rápido](#-arranque-rápido)
- [👤 Residentes del Vault](#-residentes-del-vault)
- [🎭 Diferenciación por rol](#-diferenciación-por-rol)
- [📡 API — Terminales del Vault](#-api--terminales-del-vault)
- [📮 Pruebas con Postman](#-pruebas-con-postman)
- [🧪 Tests](#-tests)
- [⚙️ CI/CD — GitHub Actions](#️-cicd--github-actions)
- [🛡️ Seguridad OWASP](#️-seguridad-owasp)
- [📁 Estructura del proyecto](#-estructura-del-proyecto)
- [🌿 Gestión de versiones con Git](#-gestión-de-versiones-con-git)

---

## ☢️ Arquitectura

```
   [ NAVEGADOR — SUPERFICIE EXTERIOR ]
            │  Puerto 5000
            ▼
  ╔═════════════════════════════╗
  ║  🖥️  TERMINAL FRONTAL       ║   <- unica entrada al Vault
  ║  Flask + Jinja2             ║      (como la puerta de la Boveda)
  ║  Renderiza UI por rol       ║
  ║  Proxy hacia la API interna ║
  ╚══════════════╤══════════════╝
                 │ Red privada appnet
                 ▼
  ╔═════════════════════════════╗
  ║  ⚙️  MAINFRAME DEL VAULT    ║   <- solo accesible desde dentro
  ║  Flask REST API             ║      (como el Overseer's Office)
  ║  JWT · bcrypt · rate limit  ║
  ║  Pool de conexiones MySQL   ║
  ╚══════════════╤══════════════╝
                 │ MySQL protocol
                 ▼
  ╔═════════════════════════════╗
  ║  🗄️  ARCHIVO DEL VAULT      ║   <- sellado, nunca expuesto
  ║  MySQL 8 · Volumen Docker   ║      (como los registros del Pip-Boy)
  ╚═════════════════════════════╝
```

Los tres servicios comparten la red privada `appnet`. Desde el exterior **solo es accesible el terminal frontal** en el puerto `5000`. El mainframe (`5001`) y el archivo (`3306`) están sellados, siguiendo el principio de **mínima exposición de superficie de ataque** ([OWASP A05](./OWASP.md#a05--security-misconfiguration)).

| Contenedor | Imagen | Puerto interno | Exterior | Descripción |
|------------|--------|---------------|----------|-------------|
| `vault-frontend` | `python:3.12-slim` | 5000 | ✅ 5000 | 🖥️ Terminal frontal del Vault |
| `vault-backend` | `python:3.12-slim` | 5001 | ☢️ sellado | ⚙️ Mainframe: JWT + bcrypt |
| `vault-mysql` | `mysql:8.0` | 3306 | ☢️ sellado | 🗄️ Archivos del Vault |

---

## 🔧 Entorno de desarrollo

Se usa `venv` para aislar las dependencias, como un Vault aísla a sus residentes.

```bash
# Construir la boveda local
python3 -m venv .venv

# Abrir la compuerta
source .venv/bin/activate          # Linux / macOS
.venv\Scripts\activate             # Windows

# Aprovisionar suministros (dependencias de test)
pip install -r tests/requirements-test.txt
```

Con el entorno activo, el Pip-Boy confirma la sesion:

```
(.venv) residente@terminal:~/vault-tec-secdevops$
```

---

## 🚀 Arranque rápido

### ⚡ Requisitos previos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — el generador de fusión del Vault
- [Git](https://git-scm.com/) — el sistema de control de versiones del Overseer

### 🔩 Secuencia de inicialización

```bash
# 1. Recuperar los planos del Vault
git clone https://github.com/TU_USUARIO/vault-tec-secdevops.git
cd vault-tec-secdevops

# 2. El archivo .env ya incluye configuracion de desarrollo
#    En produccion: cambiar secretos por valores unicos y seguros

# 3. Activar generador de fusion y sellar la boveda
docker compose up --build -d

# 4. Verificar que todos los sistemas estan operativos
docker compose ps

# 5. Acceder al terminal del Vault
open http://localhost:5000        # macOS
start http://localhost:5000       # Windows
xdg-open http://localhost:5000    # Linux
```

### 🚨 Diagnostico — Sistema dañado

```bash
# Registros del mainframe en tiempo real
docker compose logs -f

# Senal de radio al mainframe
curl http://localhost:5000/api/health

# Reinicio de emergencia — borra todos los datos del archivo
docker compose down -v && docker compose up --build -d
```

> **⚙️ Protocolo de arranque:** El mainframe reintenta conexion con el archivo hasta 30 veces con espera exponencial. Los avisos de *"MySQL no disponible"* en los primeros segundos son normales — el archivo tarda en inicializarse, como el generador de un Vault recien abierto.

---

## 👤 Residentes del Vault

Las contraseñas se procesan con **[bcrypt (rounds=12)](https://pypi.org/project/bcrypt/)** — encriptacion de grado Vault-Tec. Nunca se almacenan en texto plano ([OWASP A02](./OWASP.md#a02--cryptographic-failures)).

| Residente | Contraseña | Rango | Terminal |
|-----------|------------|-------|----------|
| 👁️ `overseer` | `Overseer2077!` | `admin` | 🟠 Ambar — control total del Vault |
| 🧍 `dweller` | `Dweller2077!` | `user` | 🟢 Verde — acceso a directivas |

---

## 🎭 Diferenciacion por rol

| Caracteristica | 👁️ Overseer (admin) | 🧍 Dweller (user) |
|----------------|---------------------|-------------------|
| Color de interfaz | 🟠 Ambar — tono Pip-Boy 3000 | 🟢 Verde fosforescente |
| Icono de cabecera | ☢️ Simbolo de radiacion | ⊙ Pip-Boy |
| Ver directivas del Vault | ✅ | ✅ |
| Crear nuevas directivas | ✅ | ❌ `403 — Acceso Denegado` |
| Panel de control del Overseer | ✅ | ❌ Redirigido al dashboard |
| Lista de residentes | ✅ | ❌ `403 — Acceso Denegado` |
| Log de auditoria | ✅ | ❌ `403 — Acceso Denegado` |
| Estadisticas del Vault | ✅ | ❌ `403 — Acceso Denegado` |
| Activar / desactivar residentes | ✅ | ❌ `403 — Acceso Denegado` |

El control de acceso se implementa con los decoradores `@token_required` y `@admin_required` en el mainframe ([`backend/app.py`](./backend/app.py)), siguiendo [OWASP A01 — Broken Access Control](./OWASP.md#a01--broken-access-control).

---

## 📡 API — Terminales del Vault

Todos los endpoints son accesibles desde `http://localhost:5000/api/` a traves del **terminal frontal**. El mainframe interno escucha en `http://localhost:5001` pero esta sellado al exterior.

Para pruebas manuales importa los dos archivos de la carpeta [`Postman/`](./Postman/) en [Postman](https://www.postman.com/). Ver instrucciones completas en la sección [📮 Pruebas con Postman](#-pruebas-con-postman).

| Metodo | Terminal | Autorizacion | Funcion |
|--------|----------|-------------|---------|
| `GET` | `/api/health` | — | 🟢 Diagnostico del sistema |
| `POST` | `/api/login` | — | 🔑 Autenticacion → JWT |
| `GET` | `/api/profile` | 🔑 JWT | 👤 Perfil del residente activo |
| `GET` | `/api/projects` | 🔑 JWT | 📋 Listar directivas del Vault |
| `POST` | `/api/projects` | 🔑 JWT Overseer | ✏️ Nueva directiva |
| `GET` | `/api/admin/users` | 🔑 JWT Overseer | 👥 Lista de residentes |
| `POST` | `/api/admin/users/<id>/toggle` | 🔑 JWT Overseer | 🔒 Activar/desactivar residente |
| `GET` | `/api/admin/logs` | 🔑 JWT Overseer | 📜 Registro de auditoria |
| `GET` | `/api/admin/stats` | 🔑 JWT Overseer | 📊 Estadisticas del Vault |

### 🟢 Terminal de diagnostico

```json
GET /api/health -> 200 OK
{
  "status": "ok",
  "service": "backend-api",
  "database": "ok",
  "engine": "MySQL 8"
}
```

### 🔑 Autenticacion

```json
POST /api/login
{ "username": "overseer", "password": "Overseer2077!" }

-> 200  { "token": "<JWT>", "username": "overseer", "role": "admin" }
-> 401  { "error": "Credenciales incorrectas" }
-> 429  { "error": "Demasiados intentos. Espera 15 minutos." }
```

---

## 📮 Pruebas con Postman

La carpeta [`Postman/`](./Postman/) contiene dos archivos listos para importar:

| Archivo | Tipo | Descripcion |
|---------|------|-------------|
| [`postman_collection.json`](./Postman/postman_collection.json) | 📋 Coleccion | 28 requests organizados en 7 carpetas con tests automaticos |
| [`vault-tec-environment.json`](./Postman/vault-tec-environment.json) | 🌍 Environment | Variables de entorno: URLs, credenciales, tokens JWT |

### ⚡ Importar al Vault de Postman

```
1. Abre Postman
2. File → Import → sube postman_collection.json
3. File → Import → sube vault-tec-environment.json
4. Selecciona el environment "☢️ Vault-Tec SecDevOps — LOCAL" (esquina superior derecha)
5. Levanta el Vault: docker compose up --build -d
6. Ejecuta P0 · Setup para obtener los tokens JWT automaticamente
```

### 🗂️ Estructura de la coleccion

```
☢️ Vault-Tec SecDevOps — API Tests
│
├── P0 · Setup — obtener tokens          (2 requests)
│   ├── Login overseer → guarda JWT en {{overseer_token}}
│   └── Login dweller  → guarda JWT en {{dweller_token}}
│
├── P1 · Autenticacion — A07             (6 requests)
│   ├── 🔴 Credenciales incorrectas → 401 con mensaje generico
│   ├── 🔴 Usuario inexistente → mismo 401 (sin user oracle)
│   ├── 🔴 JWT con firma manipulada → rechazado
│   ├── 🔴 Sin token → 401
│   ├── 🟠 Body vacio → 400
│   └── 🟠 Rate limiting — simula brute force (429)
│
├── P2 · Control de Acceso RBAC — A01   (6 requests)
│   ├── 🔴 Dweller intenta /admin/users → 403
│   ├── 🔴 Dweller intenta /admin/logs  → 403
│   ├── 🔴 Dweller intenta crear directiva → 403
│   ├── 🟢 Overseer lista residentes (sin password_hash)
│   ├── 🟢 Dweller lee directivas → 200
│   └── 🟢 Perfil overseer — rol admin confirmado
│
├── P3 · Directivas (MySQL) — CRUD       (4 requests)
│   ├── 🟢 Listar directivas desde MySQL
│   ├── 🟢 Overseer crea directiva nueva → 201 + ID
│   ├── 🟠 Sin nombre obligatorio → 400
│   └── 🟠 Estado invalido → 400
│
├── P4 · Administracion — A01/A09        (4 requests)
│   ├── 🟢 Overseer obtiene estadisticas del Vault
│   ├── 🟢 Overseer lee logs de auditoria (sin hashes)
│   ├── 🟠 Stats sin token → 401
│   └── 🟠 Stats con dweller → 403
│
├── P5 · Seguridad HTTP — A05            (3 requests)
│   ├── 🔴 Cabeceras OWASP en /api/health
│   │      X-Frame-Options · X-Content-Type-Options
│   │      X-XSS-Protection · Cache-Control · CSP
│   ├── 🔴 404 sin Traceback Python
│   └── 🔴 Inyeccion SQL en login bloqueada
│
└── P6 · Smoke Tests — flujo feliz       (3 requests)
    ├── Health check — DB MySQL ok + respuesta < 1s
    ├── Perfil dweller — datos correctos
    └── Directivas — overseer ve todas desde MySQL
```

### 🌍 Variables del environment

| Variable | Valor por defecto | Tipo | Descripcion |
|----------|------------------|------|-------------|
| `base_url` | `http://localhost:5000` | default | URL del terminal frontal (proxy) |
| `backend_url` | `http://localhost:5001` | default | URL directa al mainframe |
| `overseer_username` | `overseer` | default | Nombre del Overseer |
| `overseer_password` | `Overseer2077!` | 🔒 secret | Contrasena del Overseer |
| `dweller_username` | `dweller` | default | Nombre del Dweller |
| `dweller_password` | `Dweller2077!` | 🔒 secret | Contrasena del Dweller |
| `overseer_token` | *(vacio)* | auto | JWT admin — se rellena con P0 |
| `dweller_token` | *(vacio)* | auto | JWT user — se rellena con P0 |
| `jwt_algorithm` | `HS256` | default | Algoritmo de firma JWT |
| `jwt_expiration_hours` | `1` | default | Expiracion del token en horas |
| `rate_limit_max_attempts` | `5` | default | Intentos antes del bloqueo |
| `rate_limit_window_minutes` | `15` | default | Ventana del rate limiting |

> **🔒 Nota de seguridad:** Las variables de tipo `secret` (`overseer_password`, `dweller_password`) no aparecen en los logs de Postman ni se sincronizan con Postman Cloud.

### 🚀 Ejecucion con Collection Runner

Para ejecutar toda la suite de una vez:

```
1. Click en "☢️ Vault-Tec SecDevOps — API Tests" en la barra lateral
2. Click en "Run collection"
3. Asegurate de que el order sea: P0 → P1 → P2 → P3 → P4 → P5 → P6
4. Activa "Save responses" para ver el detalle de cada test
5. Click en "Run Vault-Tec SecDevOps"
```

> **⚠️ Importante:** Ejecuta siempre **P0 · Setup primero**. Los tokens JWT que obtiene P0 son usados por todas las carpetas siguientes. Sin ese paso, P1-P6 fallarán con 401.

---

## 🧪 Tests

Ver documentacion completa en [**TESTS.md**](./TESTS.md).

El Vault cuenta con **70 pruebas de seguridad** distribuidas en dos modulos:

| Modulo | Archivo | Tests | Descripcion |
|--------|---------|-------|-------------|
| 🔬 Laboratorio (backend) | [`tests/test_backend.py`](./tests/test_backend.py) | 45 | Unitarios + integracion con mocks |
| 🖥️ Terminal (frontend) | [`tests/test_frontend.py`](./tests/test_frontend.py) | 25 | Rutas Flask con backend mockeado |

### ⚡ Activar los protocolos de prueba

```bash
# Modulo de laboratorio — rapidos, sin base de datos
pytest tests/test_backend.py -v

# Modulo de terminal — backend simulado
pytest tests/test_frontend.py -v

# Protocolo completo con informe de cobertura
pytest tests/ -v --cov=backend --cov-report=term-missing

# Prueba por sector
pytest tests/test_backend.py -v -k "TestBcrypt"     # Sector cripto
pytest tests/test_backend.py -v -k "TestJWT"        # Sector tokens
pytest tests/test_backend.py -v -k "TestRateLimit"  # Sector defensa
```

### 🏚️ Niveles de seguridad del Vault

```
☢️  NIVEL 1 — Pruebas de laboratorio (sin red ni BD)
  ├── 🔐 bcrypt: hash, salt aleatorio, verificacion, timing attacks
  ├── 🎫 JWT: generacion, verificacion, expiracion, firma manipulada
  └── 🚨 Rate limiting: ventana 15 min, aislamiento por IP

⚙️  NIVEL 2 — Simulacros de terminal (MySQL mockeado)
  ├── 💓 /api/health: sistema OK y modo degradado (503)
  ├── 🔑 /api/login: credenciales, rate limit, cuenta inactiva (403)
  ├── 👤 /api/profile: token valido, expirado, sin token
  └── 📋 /api/projects: listado, creacion, acceso denegado

🛡️  NIVEL 3 — Protocolos de seguridad (cabeceras OWASP)
  ├── 🪖 Cabeceras HTTP: X-Frame-Options, CSP, Cache-Control
  ├── 🚪 Control de acceso: 401 sin credencial, 403 sin rango
  └── ⏱️  Tokens expirados: rechazados con 401

🖥️  NIVEL 4 — Terminal frontal (backend simulado)
  ├── 🚶 Rutas publicas: redirecciones sin sesion activa
  ├── 🔑 Flujo de login: exito, error, rate limit, sesion activa
  ├── 📊 Dashboard: diferenciacion Overseer/Dweller, token expirado
  ├── 👁️  Panel del Overseer: acceso admin, bloqueo a dwellers
  └── 📡 Proxy API: health, login, mainframe no disponible
```

---

## ⚙️ CI/CD — GitHub Actions

Pipeline definido en [`.github/workflows/ci.yml`](./.github/workflows/ci.yml). Se activa automaticamente en cada **push** y **pull request** a `main` y `develop`.

```
📤 push / pull_request -> main, develop
         │
         ├── 🧪 test ─────────────── 70 tests sin BD
         │         └── ok ─────────── 🐳 docker (build + smoke test)
         │                   └── ok + main ── 🚀 deploy
         │
         ├── 🗄️  test-mysql ────────── Integracion con MySQL 8 real
         │              (continue-on-error — no bloquea)
         │
         └── 🔍 security ──────────── Bandit SAST
```

| Job | Mision | Bloquea deploy |
|-----|--------|---------------|
| 🧪 `test` | 70 tests unitarios + frontend | ✅ Si |
| 🗄️ `test-mysql` | Integracion con MySQL 8 real | ❌ No |
| 🔍 `security` | Bandit — analisis estatico SAST | ❌ No |
| 🐳 `docker` | Build imagenes + smoke test stack | ✅ Si |
| 🚀 `deploy` | Deploy a produccion (solo `main`) | Solo en `main` |

---

## 🛡️ Seguridad OWASP

Ver analisis completo en [**OWASP.md**](./OWASP.md).

El Vault implementa medidas del [**OWASP Top Ten 2021**](https://owasp.org/www-project-top-ten/) y del [**OWASP API Security Top Ten**](https://owasp.org/www-project-api-security/) — porque en el Yermo, los Raiders no esperan a que parchees tus vulnerabilidades.

| ID | Amenaza | Protocolo de defensa | Terminal |
|----|---------|---------------------|----------|
| [A01](./OWASP.md#a01--broken-access-control) | 🚪 Broken Access Control | `@token_required` + `@admin_required`; rutas selladas redirigen al login | [`backend/app.py`](./backend/app.py) · [`frontend/app.py`](./frontend/app.py) |
| [A02](./OWASP.md#a02--cryptographic-failures) | 🔐 Cryptographic Failures | **bcrypt rounds=12** — mas lento que SHA-256, los Raiders tardan siglos | [`backend/app.py`](./backend/app.py) |
| [A03](./OWASP.md#a03--injection) | 💉 Injection | Queries parametrizadas con `%s` — ningun Raider inyecta SQL en el Vault | [`backend/app.py`](./backend/app.py) |
| [A04](./OWASP.md#a04--insecure-design) | ⚠️ Insecure Design | Pool acotado (`pool_size=5`); reintentos con espera exponencial | [`backend/app.py`](./backend/app.py) |
| [A05](./OWASP.md#a05--security-misconfiguration) | ⚙️ Security Misconfiguration | Mainframe y archivo sellados; solo el terminal frontal en el exterior | [`docker-compose.yml`](./docker-compose.yml) |
| [A07](./OWASP.md#a07--identification-and-authentication-failures) | 🔑 Auth Failures | Rate limit 5/15min por IP; tokens JWT de 1h; logout limpia sesion | [`backend/app.py`](./backend/app.py) |
| [A08](./OWASP.md#a08--software-and-data-integrity-failures) | 📦 Data Integrity | Hash nunca expuesto en respuestas; registro como admin bloqueado | [`backend/app.py`](./backend/app.py) |
| [A09](./OWASP.md#a09--security-logging-and-monitoring-failures) | 📜 Logging & Monitoring | `audit_log` en MySQL: login, acciones admin, IP, timestamp — el diario del Overseer | [`backend/app.py`](./backend/app.py) |
| [A05 HTTP](./OWASP.md#cabeceras-de-seguridad-http) | 🪖 Security Headers | `X-Frame-Options: DENY`, `CSP`, `X-XSS-Protection`, `Cache-Control: no-store` | [`backend/app.py`](./backend/app.py) · [`frontend/app.py`](./frontend/app.py) |

---

## 📁 Estructura del proyecto

```
vault-tec-secdevops/              <- Bóveda principal
├── backend/                      <- ⚙️  Mainframe del Vault
│   ├── app.py                       API: JWT, bcrypt, MySQL, rate limit, audit
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                     <- 🖥️  Terminal de acceso
│   ├── app.py                       Web: sesiones, proxy API, control por rol
│   ├── requirements.txt
│   ├── Dockerfile
│   └── templates/
│       ├── base.html                Layout CRT Fallout (scanlines, phosphor glow)
│       ├── login.html               Terminal de autenticacion del Vault
│       ├── dashboard.html           Panel Overseer 🟠 / Dweller 🟢
│       ├── admin.html               Cuartel general del Overseer
│       └── new_project.html         Nueva directiva del Vault
├── mysql/
│   └── init.sql                  <- 🗄️  Inicializacion del archivo
├── tests/
│   ├── conftest.py               <- 🔧 Configuracion del protocolo de pruebas
│   ├── test_backend.py           <- 🔬 45 tests: bcrypt, JWT, rate limit, endpoints
│   ├── test_frontend.py          <- 🖥️  25 tests: rutas, flujos, roles, proxy
│   └── requirements-test.txt
├── Postman/
│   ├── postman_collection.json   <- 📮 28 requests en 7 carpetas con tests OWASP
│   └── vault-tec-environment.json   🌍 Variables: URLs, credenciales, tokens JWT
├── .github/workflows/
│   └── ci.yml                    <- 🤖 Pipeline: test -> docker -> deploy
├── docker-compose.yml            <- 🏗️  Planos de construccion del Vault
├── .env                          <- 🔑 Codigos de acceso (no subir en produccion)
├── .env.example                     Plantilla de codigos requeridos
├── README.md
├── OWASP.md                      <- 🛡️  Informe de seguridad OWASP
└── TESTS.md                      <- 🧪 Documentacion de protocolos de prueba
```

---

## 🌿 Gestion de versiones con Git

```
main        <- 🟢 Vault sellado y estable (requiere PR + CI verde)
develop     <- 🟡 Zona de pruebas del Overseer
feature/*   <- 🔵 Nuevas instalaciones del Vault
fix/*       <- 🔴 Reparaciones de emergencia
```

```bash
# Abrir nueva instalacion desde la zona de pruebas
git checkout -b feature/nueva-funcionalidad develop

# Registrar cambios en el diario del Overseer (Conventional Commits)
git commit -m "feat: añadir terminal de estadisticas"
git commit -m "fix: corregir rate limiting por IP del Yermo"
git commit -m "test: cubrir endpoint toggle de residentes"
git commit -m "docs: actualizar mapa del Vault en README"
git commit -m "chore: limpiar suministros no utilizados"

# Pull Request -> revision del Overseer -> merge
# develop -> main cuando el Vault esta estable
```

---

<div align="center">

```
  ╔══════════════════════════════════════════════╗
  ║   ☢️  VAULT-TEC CORPORATION — VAULT 33  ☢️   ║
  ║   Desarrollado por Jose · CEU San Pablo      ║
  ║   Puesta en Produccion Segura · 2077         ║
  ╚══════════════════════════════════════════════╝
```

[![OWASP Top 10](https://img.shields.io/badge/OWASP-Top%2010%20Compliant-orange)](./OWASP.md)
[![Tests](https://img.shields.io/badge/Tests-70%20passing-success)](./TESTS.md)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](docker-compose.yml)
[![War](https://img.shields.io/badge/☢️%20War-Never%20Changes-black)](https://fallout.fandom.com/wiki/Fallout)

*"Please stand by."*

</div>
