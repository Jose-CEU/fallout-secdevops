# Fallout SecDevOps - Vault 33

Aplicación web temática de Fallout desarrollada como práctica de Puesta en Producción Segura.

## Arquitectura

- **Frontend**: Flask (Python) — puerto 5000
- **Backend**: Flask API REST (Python) — puerto 5001
- **Base de datos**: MySQL 8

## Entorno de desarrollo

Se ha utilizado un **entorno virtual de Python (venv)** para aislar las dependencias del proyecto.

### Activación del entorno virtual
```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
```

> 📸 Captura del prompt con el entorno virtual activo:
> *(insertar captura de pantalla aquí)*

## Cómo ejecutar el proyecto
```bash
docker-compose up --build
```

Accede a: http://localhost:5000

### Usuarios de prueba

| Usuario | Contraseña | Rol |
|---|---|---|
| overseer | overseer_admin_2024 | admin |
| dweller | dweller_user_2024 | user |

---

## 📡 API Endpoints

El backend expone los siguientes endpoints en `http://localhost:5001`:

### GET /api/status
Comprueba que el backend está activo.

**Respuesta:**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

### GET /api/vault
Devuelve el estado actual del vault desde la base de datos.

**Respuesta:**
```json
{
  "vault_status": "Secure",
  "radiation_level": "Low"
}
```

---

### POST /api/register
Registra un nuevo usuario con rol `user`.

**Body:**
```json
{
  "username": "nuevo_usuario",
  "password": "minimo6caracteres"
}
```

**Respuestas:**
| Código | Descripción |
|---|---|
| 201 | Usuario creado correctamente |
| 400 | Faltan campos o contraseña muy corta |
| 409 | El usuario ya existe |
| 500 | Error de base de datos |

---

### POST /api/login
Autentica un usuario y devuelve su rol.

**Body:**
```json
{
  "username": "overseer",
  "password": "overseer_admin_2024"
}
```

**Respuesta exitosa:**
```json
{
  "message": "Login successful",
  "username": "overseer",
  "role": "admin"
}
```

**Respuestas:**
| Código | Descripción |
|---|---|
| 200 | Login correcto |
| 400 | Faltan campos |
| 401 | Credenciales incorrectas |
| 500 | Error de base de datos |

## Tests

### Tests unitarios
Comprueban funciones individuales sin dependencias externas:
- `test_unit.py` — verifica el endpoint `/api/status` y su respuesta JSON

### Tests de integración
Comprueban la comunicación entre componentes con base de datos real:
- `test_auth.py` — registro y login de usuarios contra MySQL
- `test_backend.py` — verificación del estado de la API

### Ejecutar tests
```bash
cd backend
pytest
```

## CI/CD

GitHub Actions ejecuta automáticamente los tests en cada push y pull request a `main`.
Ver `.github/workflows/ci.yml`

## Seguridad OWASP

Ver archivo [OWASP.md](./OWASP.md)