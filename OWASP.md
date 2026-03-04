# OWASP Top Ten - Medidas aplicadas

## OWASP Web Application Top Ten

### A01 - Broken Access Control
- El dashboard requiere sesión activa. Sin login redirige a `/login`.
- Los roles `admin` y `user` están diferenciados en sesión Flask.

### A02 - Cryptographic Failures
- Las contraseñas se almacenan hasheadas con `werkzeug` (bcrypt).
- La `SECRET_KEY` de Flask se carga desde variable de entorno, nunca hardcodeada.
- El archivo `.env` está en `.gitignore` y nunca se sube al repositorio.

### A03 - Injection
- Todas las consultas SQL usan parámetros con `%s` (consultas parametrizadas).
- No se concatenan strings en ninguna query.

### A04 - Insecure Design
- Separación clara entre frontend y backend en contenedores distintos.
- El backend no expone datos sensibles en sus respuestas JSON.

### A05 - Security Misconfiguration
- Los contenedores están configurados con variables de entorno.
- MySQL no es accesible desde fuera de la red Docker salvo el puerto mapeado.

### A06 - Vulnerable and Outdated Components
- Se usan imágenes oficiales de Python 3.11 y MySQL 8.
- Las dependencias están fijadas en `requirements.txt`.

### A07 - Identification and Authentication Failures
- Contraseñas con mínimo 6 caracteres validadas en backend.
- Sesiones Flask con `SECRET_KEY` segura.
- Logout limpia completamente la sesión con `session.clear()`.

### A09 - Security Logging and Monitoring Failures
- Los errores de base de datos se registran con `print()` en consola del contenedor.
- Los errores HTTP devuelven códigos correctos (400, 401, 409, 500).

---

## OWASP API Security Top Ten

### API1 - Broken Object Level Authorization
- Los endpoints de la API validan que los datos requeridos estén presentes antes de procesar.

### API2 - Broken Authentication
- El endpoint `/api/login` valida credenciales contra hash almacenado en base de datos.
- Responde con 401 ante credenciales incorrectas.

### API3 - Broken Object Property Level Exposure
- La API solo devuelve los campos necesarios, nunca el hash de la contraseña.

### API4 - Unrestricted Resource Consumption
- El backend tiene un límite de reintentos de conexión a base de datos (5 intentos).

### API8 - Security Misconfiguration
- El backend corre en contenedor aislado.
- Las credenciales de base de datos se pasan por variables de entorno.

### API10 - Unsafe Consumption of APIs
- El frontend valida que la respuesta del backend sea correcta antes de renderizar.