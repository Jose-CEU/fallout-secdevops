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