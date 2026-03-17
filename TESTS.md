# Documentación de Tests — Vault-Tec SecDevOps

## Estrategia de pruebas

Se sigue la pirámide de testing con dos ficheros especializados:

```
           /\
          /  \   test_frontend.py
         / 25 \  Rutas Flask + flujos con backend mockeado
        /------\
       /        \ test_backend.py
      /    45    \ Unitarios puros + integración HTTP + seguridad
     /____________\
```

| Fichero | Tests | Requiere DB | Velocidad |
|---------|:-----:|:-----------:|:---------:|
| `test_backend.py` | 45 | No (MySQL mockeado) | ~2s |
| `test_frontend.py` | 25 | No (backend mockeado con `responses`) | ~3s |
| **Total** | **70** | — | **~5s** |

---

## Ejecución

```bash
# Activar entorno virtual
source .venv/bin/activate

# Instalar dependencias de test
pip install -r tests/requirements-test.txt

# Todos los tests
pytest tests/ -v

# Solo backend
pytest tests/test_backend.py -v

# Solo frontend
pytest tests/test_frontend.py -v

# Con cobertura de código
pytest tests/ -v --cov=backend --cov-report=term-missing

# Parar al primer fallo
pytest tests/ -x -v
```

---

## `test_backend.py` — 45 tests

### Nivel 1: Unitarias puras — bcrypt (7 tests)

Verifican que el hash de contraseñas cumple los requisitos de seguridad sin necesitar red ni BD.

| Test | Qué verifica | OWASP |
|------|-------------|-------|
| `test_hash_nunca_es_texto_plano` | El hash difiere del password original | A02 |
| `test_hash_tiene_prefijo_bcrypt` | El hash empieza con `$2b$` (formato bcrypt) | A02 |
| `test_verificacion_correcta` | `verify_password` devuelve True con password correcto | A02 |
| `test_verificacion_incorrecta` | `verify_password` devuelve False con password incorrecto | A02 |
| `test_salt_aleatorio_hashes_distintos` | Dos hashes del mismo password son distintos (salt único) | A02 |
| `test_ambos_hashes_verifican` | Ambos hashes distintos verifican correctamente | A02 |
| `test_hash_no_contiene_password_en_claro` | El password no aparece en el hash | A02 |

### Nivel 1: Unitarias puras — JWT (5 tests)

| Test | Qué verifica | OWASP |
|------|-------------|-------|
| `test_token_overseer_contiene_rol_admin` | Payload incluye user, role y sub correctos | A07 |
| `test_token_dweller_contiene_rol_user` | Token de dweller tiene role=user | A01 |
| `test_token_invalido_lanza_excepcion` | String arbitrario lanza InvalidTokenError | A07 |
| `test_token_manipulado_rechazado` | Firma modificada invalida el token | A02 |
| `test_token_contiene_expiracion` | Payload incluye `exp` e `iat` | A07 |

### Nivel 1: Unitarias puras — Rate limiting (4 tests)

| Test | Qué verifica | OWASP |
|------|-------------|-------|
| `test_cinco_intentos_permitidos` | Los primeros 5 intentos por IP pasan | A07 |
| `test_sexto_intento_bloqueado` | El 6º intento desde la misma IP devuelve False | A07 |
| `test_ips_distintas_son_independientes` | El bloqueo no afecta a otras IPs | A07 |
| `test_bloqueo_no_afecta_a_otras_ips` | IPs distintas tienen contadores independientes | A07 |

### Nivel 2: Integración HTTP — `/api/health` (2 tests)

| Test | Qué verifica |
|------|-------------|
| `test_health_ok_con_db_disponible` | 200 con `status=ok` y `engine=MySQL 8` |
| `test_health_devuelve_503_si_db_falla` | 503 cuando MySQL no responde |

### Nivel 2: Integración HTTP — `/api/login` (7 tests)

| Test | Qué verifica | OWASP |
|------|-------------|-------|
| `test_login_overseer_correcto` | 200 + token JWT + role=admin | A07 |
| `test_login_dweller_correcto` | 200 + token JWT + role=user | A07 |
| `test_login_password_incorrecto_devuelve_401` | 401 con password malo | A07 |
| `test_login_usuario_inexistente_devuelve_401` | 401 (mismo código que password malo) | A07 |
| `test_login_rate_limit_devuelve_429` | 429 cuando `check_rate_limit` devuelve False | A07 |
| `test_login_body_vacio_devuelve_400` | 400 sin campos requeridos | A08 |
| `test_login_cuenta_inactiva_devuelve_403` | 403 para cuentas desactivadas | A07 |

### Nivel 2: Integración HTTP — `/api/profile` (3 tests)

| Test | Qué verifica | OWASP |
|------|-------------|-------|
| `test_profile_sin_token_devuelve_401` | 401 sin JWT | A01 |
| `test_profile_con_token_overseer` | 200 con username y role correctos | A01 |
| `test_profile_no_expone_password_hash` | Respuesta sin `password_hash` ni `password` | A08 |

### Nivel 2: Integración HTTP — `/api/projects` (6 tests)

| Test | Qué verifica | OWASP |
|------|-------------|-------|
| `test_listar_directivas_con_token` | 200 + array de proyectos | A01 |
| `test_listar_directivas_sin_token_devuelve_401` | 401 sin JWT | A01 |
| `test_crear_directiva_admin_ok` | 201 + ID asignado | A01 |
| `test_crear_directiva_sin_nombre_devuelve_400` | 400 por campo requerido | A08 |
| `test_crear_directiva_usuario_normal_devuelve_403` | 403 para rol user | A01 |
| `test_crear_directiva_estado_invalido_devuelve_400` | 400 por estado no permitido | A08 |

### Nivel 3: Endpoints de administración (7 tests)

| Test | Qué verifica | OWASP |
|------|-------------|-------|
| `test_listar_residentes_sin_token_devuelve_401` | 401 sin JWT | A01 |
| `test_listar_residentes_dweller_devuelve_403` | 403 para rol user | A01 |
| `test_listar_residentes_overseer_ok` | 200 + sin `password_hash` en ningún usuario | A01/A08 |
| `test_logs_overseer_ok` | 200 + array de logs | A09 |
| `test_logs_dweller_devuelve_403` | 403 para rol user | A01 |
| `test_stats_overseer_ok` | 200 con campos `users`, `projects` | A09 |
| `test_toggle_residente_overseer_ok` | 200 al activar/desactivar | A01 |
| `test_toggle_residente_inexistente_devuelve_404` | 404 para ID que no existe | A08 |

### Nivel 4: Seguridad HTTP — cabeceras (3 tests)

| Test | Qué verifica | OWASP |
|------|-------------|-------|
| `test_cabeceras_owasp_presentes` | X-Frame-Options, X-Content-Type-Options, Cache-Control, CSP | A05 |
| `test_ruta_inexistente_devuelve_404_json` | 404 sin stack trace Python | A05 |
| `test_token_jwt_expirado_devuelve_401` | Token con `exp` en el pasado → 401 | A07 |

---

## `test_frontend.py` — 25 tests

### Rutas públicas sin sesión (8 tests)

| Test | Qué verifica |
|------|-------------|
| `test_raiz_redirige_a_login` | `/` → 302 a `/login` |
| `test_login_get_devuelve_200` | Página de login accesible |
| `test_login_muestra_terminal_vault_tec` | Contenido Vault-Tec en el HTML |
| `test_login_muestra_credenciales_demo` | Muestra overseer y dweller |
| `test_dashboard_sin_sesion_redirige` | `/dashboard` → 302 |
| `test_admin_sin_sesion_redirige` | `/admin` → 302 |
| `test_new_project_sin_sesion_redirige` | `/admin/new-project` → 302 |
| `test_login_campos_vacios_muestra_error` | Error de validación visible |

### Flujo de login (6 tests)

| Test | Qué verifica | OWASP |
|------|-------------|-------|
| `test_login_overseer_redirige_a_dashboard` | 302 a dashboard con token válido | A07 |
| `test_login_dweller_redirige_a_dashboard` | 302 a dashboard | A07 |
| `test_login_credenciales_incorrectas_muestra_error` | Mensaje de error visible | A07 |
| `test_login_rate_limit_muestra_aviso` | Aviso de rate limiting visible | A07 |
| `test_login_con_sesion_activa_redirige_a_dashboard` | Sin doble login | A07 |
| `test_logout_limpia_sesion` | Sesión eliminada, dashboard redirige | A07 |

### Dashboard diferenciado por rol (4 tests)

| Test | Qué verifica | OWASP |
|------|-------------|-------|
| `test_dashboard_overseer_muestra_estadisticas` | Panel ámbar con stats | A01 |
| `test_dashboard_dweller_no_muestra_panel_admin` | Sin botones admin | A01 |
| `test_dashboard_muestra_directivas` | Nombre de proyecto visible | Func |
| `test_dashboard_token_expirado_redirige_a_login` | 302 a login si backend devuelve 401 | A07 |

### Panel admin — control de acceso (4 tests)

| Test | Qué verifica | OWASP |
|------|-------------|-------|
| `test_admin_overseer_puede_acceder` | 200 para overseer | A01 |
| `test_admin_dweller_redirigido` | 302 para dweller | A01 |
| `test_nueva_directiva_overseer_ok` | 302 tras crear directiva | A01 |
| `test_nueva_directiva_dweller_redirigido` | 302 para dweller | A01 |

### Proxy API (3 tests)

| Test | Qué verifica |
|------|-------------|
| `test_proxy_health` | Proxy devuelve health del backend |
| `test_proxy_login` | Proxy reenvía login al backend |
| `test_proxy_backend_no_disponible` | 503 si el backend no responde |

---

## Cobertura de OWASP por tests

| Control | `test_backend.py` | `test_frontend.py` |
|---------|:-----------------:|:-----------------:|
| A01 Broken Access Control | ✅ 12 tests | ✅ 8 tests |
| A02 Cryptographic Failures | ✅ 7 tests | — |
| A03 Injection | — | — |
| A04 Insecure Design | — | — |
| A05 Security Misconfiguration | ✅ 3 tests | — |
| A07 Authentication Failures | ✅ 14 tests | ✅ 6 tests |
| A08 Data Integrity | ✅ 5 tests | — |
| A09 Logging & Monitoring | ✅ 2 tests | — |

> A03 e A04 se cubren en las pruebas Postman (test de inyección SQL) y en el OWASP.md, donde se documenta el diseño seguro.
