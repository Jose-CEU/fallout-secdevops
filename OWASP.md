# OWASP Top 10 — Controles implementados en Vault-Tec SecDevOps

Documento de trazabilidad entre los riesgos del OWASP Top 10 2021 (Web) y el OWASP API Security Top 10 2023, y los controles técnicos aplicados en el proyecto.

---

## OWASP Web Application Top 10

### A01 — Broken Access Control ✅

**Riesgo:** Un usuario accede a recursos o ejecuta acciones para las que no tiene permiso.

**Controles implementados:**

| Control | Ubicación | Detalle |
|---------|-----------|---------|
| JWT obligatorio en rutas protegidas | `backend/app.py` · `@token_required` | Devuelve 401 si no hay token o es inválido |
| RBAC por rol en endpoints admin | `backend/app.py` · `@admin_required` | Devuelve 403 si `role != "admin"` |
| Frontend verifica rol antes de renderizar | `frontend/app.py` | Redirige a dashboard si dweller intenta acceder a `/admin` |
| Sin escalada de privilegios | `backend/app.py` · `init_db()` | El rol se asigna en el seed; no hay endpoint para cambiarlo |

```python
# backend/app.py — decorador admin_required
def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if request.current_user.get("role") != "admin":
            return jsonify({"error": "Acceso denegado: se requiere rol admin"}), 403
        return f(*args, **kwargs)
    return decorated
```

---

### A02 — Cryptographic Failures ✅

**Riesgo:** Exposición de datos sensibles por criptografía débil o ausente.

**Controles implementados:**

| Control | Detalle |
|---------|---------|
| bcrypt para contraseñas | `rounds=12` (~250ms/hash). Resiste ataques GPU. Salt automático por llamada |
| JWT firmado con HS256 | Clave cargada de variable de entorno; expiración 1 hora |
| `SECRET_KEY` de entorno | Nunca hardcodeada en código. Falla al arrancar si no está definida |
| Respuestas sin `password_hash` | `SELECT id, username, role, active, created_at` — el hash nunca sale de la BD |
| `.env` en `.gitignore` | Secretos no versionados |

```python
# backend/app.py — hash bcrypt
def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(rounds=12)     # salt aleatorio en cada llamada
    ).decode("utf-8")
```

---

### A03 — Injection ✅

**Riesgo:** Datos no confiables inyectados en intérpretes (SQL, shell, etc.).

**Controles implementados:**

| Control | Detalle |
|---------|---------|
| Consultas SQL parametrizadas | Toda query usa `%s` con tupla separada. Sin concatenación de strings |
| Truncado de inputs | `username[:64]`, `password[:128]`, `name[:128]`, `description[:500]` |
| Jinja2 auto-escape | Activo por defecto; ninguna variable se renderiza sin escapar |

```python
# backend/app.py — consulta parametrizada
cur.execute(
    "SELECT id, username, password_hash, role, active "
    "FROM users WHERE username = %s",   # placeholder, nunca f-string
    (username,)                          # tupla separada
)
```

---

### A04 — Insecure Design ✅

**Riesgo:** Ausencia de controles de seguridad en el diseño de la aplicación.

**Controles implementados:**

- Separación frontend / backend en contenedores distintos con roles bien definidos.
- Backend sin interfaz HTML: solo devuelve JSON. El frontend solo gestiona sesiones y HTML.
- MySQL no accesible desde fuera de la red Docker (`expose` en lugar de `ports`).
- Pool de conexiones con tamaño máximo (`pool_size=5`) para limitar el consumo de recursos.
- Tabla `audit_log` diseñada desde el inicio para trazabilidad de seguridad.

---

### A05 — Security Misconfiguration ✅

**Riesgo:** Configuraciones inseguras por defecto o incompletas.

**Cabeceras HTTP en todas las respuestas:**

| Cabecera | Valor | Propósito |
|----------|-------|-----------|
| `X-Frame-Options` | `DENY` | Previene clickjacking |
| `X-Content-Type-Options` | `nosniff` | Evita MIME sniffing |
| `X-XSS-Protection` | `1; mode=block` | Filtro XSS del navegador |
| `Strict-Transport-Security` | `max-age=31536000` | Fuerza HTTPS en producción |
| `Content-Security-Policy` | `default-src 'self'` | Restringe origen de recursos |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Limita información del referrer |
| `Cache-Control` | `no-store` | Evita cacheo de respuestas sensibles |

**Otras medidas:**

- Contenedores ejecutan usuario no-root (`appuser`).
- Backend nunca en modo `debug`.
- Errores controlados: 404, 401, 403, 429, 500 devuelven JSON sin stack traces.

---

### A06 — Vulnerable and Outdated Components ✅

**Riesgo:** Uso de librerías o imágenes con vulnerabilidades conocidas.

**Controles implementados:**

- Versiones fijadas con `==` en todos los `requirements.txt`.
- Imágenes Docker con versión explícita (`python:3.12-slim`, `mysql:8.0`).
- Pipeline CI ejecuta `pip-audit` en cada push para detectar CVEs.
- Análisis estático con Bandit en cada push.

---

### A07 — Identification and Authentication Failures ✅

**Riesgo:** Fallos en la identificación o autenticación de usuarios.

**Controles implementados:**

| Control | Detalle |
|---------|---------|
| Rate limiting | Máximo 5 intentos por IP en ventana de 15 minutos → 429 |
| bcrypt en tiempo constante | `checkpw` no revela si el usuario existe por diferencia de tiempo |
| Respuesta idéntica | Usuario inexistente y contraseña incorrecta devuelven el mismo 401 y mensaje |
| Usuario inactivo | Cuenta desactivada → 403 aunque la contraseña sea correcta |
| JWT con expiración | 1 hora. Token expirado → 401 |
| Sesión Flask segura | `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SAMESITE=Lax` |

```python
# backend/app.py — anti timing attack
dummy_hash = "$2b$12$" + "x" * 53
stored     = row["password_hash"] if row else dummy_hash
valid      = row is not None and verify_password(password, stored)
```

---

### A08 — Software and Data Integrity Failures ✅

**Riesgo:** Código o datos sin verificación de integridad.

**Controles implementados:**

- Inputs truncados antes de procesarse (`[:64]`, `[:128]`, `[:500]`).
- Validación de estados permitidos en proyectos (`{"activo", "en revisión", "completado", "cancelado"}`).
- `SELECT` explícito de columnas — nunca `SELECT *`.
- El rol nunca proviene de datos del cliente; se toma siempre del JWT firmado.

---

### A09 — Security Logging and Monitoring Failures ✅

**Riesgo:** Ausencia de logs que permitan detectar y responder a incidentes.

**Controles implementados:**

- Tabla `audit_log` en MySQL: registra `username`, `action`, `ip`, `detail`, `created_at`.
- Eventos auditados: `login_success`, `login_failed`, `login_blocked`, `login_rate_limited`, `get_projects`, `create_project`, `list_users`, `user_activated`, `user_deactivated`.
- Endpoint `/api/admin/logs` para que el overseer consulte los últimos 100 eventos.
- Logs del servidor via `app.logger` con niveles INFO / WARNING / ERROR.
- Los logs **nunca** incluyen contraseñas ni tokens.

---

### A10 — Server-Side Request Forgery (SSRF) ✅

**Riesgo:** El servidor realiza peticiones a URLs controladas por el atacante.

**Controles implementados:**

- El backend no acepta URLs como parámetro de ningún endpoint.
- `BACKEND_URL` del frontend se configura exclusivamente via variable de entorno; el usuario nunca puede influir en él.
- No hay llamadas a servicios externos iniciadas por datos del cliente.

---

## OWASP API Security Top 10 (2023)

| ID | Riesgo | Control en Vault-Tec |
|----|--------|----------------------|
| API1 | Broken Object Level Authorization | JWT valida identidad; usuarios no pueden acceder a datos de otros |
| API2 | Broken Authentication | bcrypt + JWT HS256 + expiración + rate limiting |
| API3 | Broken Object Property Level Exposure | `SELECT` explícito sin `password_hash`. Respuestas con campos mínimos |
| API4 | Unrestricted Resource Consumption | Rate limiting en login. Pool MySQL `pool_size=5`. Inputs truncados |
| API5 | Broken Function Level Authorization | `@admin_required` en todos los endpoints administrativos |
| API6 | Unrestricted Access to Sensitive Business Flows | Crear proyectos requiere admin. No hay endpoints de escritura masiva |
| API7 | Server Side Request Forgery | Backend no acepta URLs externas. `BACKEND_URL` solo desde entorno |
| API8 | Security Misconfiguration | Cabeceras HTTP completas. Sin debug. Contenedores no-root |
| API9 | Improper Inventory Management | Todos los endpoints documentados en README. Sin versiones antiguas |
| API10 | Unsafe Consumption of APIs | Frontend valida respuestas del backend. Timeout de 8s en todas las llamadas |

---

## Matriz de cobertura por capa

| Control OWASP | Backend | Frontend | Docker | CI/CD |
|---------------|:-------:|:--------:|:------:|:-----:|
| A01 RBAC | ✅ | ✅ | — | — |
| A02 Criptografía | ✅ | — | — | — |
| A03 Inyección | ✅ | ✅ | — | — |
| A04 Diseño seguro | ✅ | ✅ | ✅ | — |
| A05 Configuración | ✅ | ✅ | ✅ | ✅ |
| A06 Componentes | ✅ | ✅ | ✅ | ✅ |
| A07 Autenticación | ✅ | ✅ | — | — |
| A08 Integridad | ✅ | — | — | — |
| A09 Logging | ✅ | — | — | ✅ |
| A10 SSRF | ✅ | ✅ | — | — |
