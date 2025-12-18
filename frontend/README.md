# Arteterapia Frontend

Frontend básico en Vanilla JavaScript que consume la API REST de Arteterapia.

## 📋 Características

- ✅ **Autenticación JWT** - Login con tokens de acceso y refresh automático
- ✅ **Gestión de Talleres** - Crear, editar, eliminar y ver talleres
- ✅ **Gestión de Participantes** - CRUD completo de participantes
- ✅ **Diseño Responsivo** - Funciona en desktop y móvil
- ✅ **Notificaciones Toast** - Feedback visual de acciones
- ✅ **Modales Dinámicos** - Formularios en modales reutilizables
- ✅ **Manejo de Errores** - Gestión robusta de errores de API

## 🚀 Inicio Rápido

### Requisitos Previos

1. **Backend ejecutándose**: El servidor Flask debe estar corriendo en `http://localhost:5000`
2. **API habilitada**: Asegúrate de que la API esté configurada correctamente

### Opción 1: Servidor HTTP Simple (Python)

```bash
# Navega a la carpeta frontend
cd frontend

# Inicia un servidor HTTP simple
python -m http.server 8000
```

Luego abre tu navegador en: `http://localhost:8000`

### Opción 2: Live Server (VS Code)

1. Instala la extensión "Live Server" en VS Code
2. Click derecho en `index.html`
3. Selecciona "Open with Live Server"

### Opción 3: Cualquier servidor web

Puedes usar cualquier servidor web estático (nginx, Apache, etc.) apuntando a la carpeta `frontend`.

## 📁 Estructura del Proyecto

```
frontend/
├── index.html              # Página principal con todas las vistas
├── css/
│   └── styles.css         # Estilos completos con sistema de diseño
└── js/
    ├── config.js          # Configuración de API y constantes
    ├── api.js             # Cliente HTTP con manejo de tokens
    ├── auth.js            # Módulo de autenticación
    ├── ui.js              # Utilidades de UI (modals, toasts, etc.)
    ├── workshops.js       # Gestión de talleres
    ├── participants.js    # Gestión de participantes
    └── app.js             # Punto de entrada y event listeners
```

## 🎨 Diseño

El frontend sigue los mismos principios de diseño que la aplicación web:

- **Minimalista**: Interfaz limpia y sin desorden
- **Colores de Marca**: Aplicados a bordes, sombras y acentos
- **Responsive**: Diseño mobile-first con Bootstrap-like grid
- **Accesible**: Estados de foco y navegación por teclado
- **Animaciones Sutiles**: Transiciones suaves para mejor UX

### Variables CSS

Todas las variables de diseño están definidas en `:root` en `styles.css`:

```css
--primary-color: #2563eb;
--success: #10b981;
--error: #ef4444;
--spacing-md: 1rem;
--radius-md: 0.5rem;
/* ... y más */
```

## 🔐 Autenticación

### Flujo de Login

1. Usuario ingresa credenciales
2. Frontend envía POST a `/api/v1/auth/login`
3. Backend retorna `access_token` y `refresh_token`
4. Tokens se guardan en `localStorage`
5. Todas las peticiones incluyen `Authorization: Bearer <token>`

### Refresh Automático

El cliente API detecta respuestas 401 y automáticamente:
1. Intenta refrescar el token usando el `refresh_token`
2. Si tiene éxito, reintenta la petición original
3. Si falla, redirige al login

### Credenciales por Defecto

```
Usuario: admin
Contraseña: admin123
```

⚠️ **Cambiar inmediatamente en producción**

## 🔌 API Endpoints Utilizados

### Autenticación
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Usuario actual

### Talleres
- `GET /api/v1/workshops` - Listar talleres
- `POST /api/v1/workshops` - Crear taller
- `GET /api/v1/workshops/{id}` - Detalle de taller
- `PATCH /api/v1/workshops/{id}` - Actualizar taller
- `DELETE /api/v1/workshops/{id}` - Eliminar taller

### Participantes
- `GET /api/v1/participants/workshop/{id}` - Listar participantes
- `POST /api/v1/participants` - Crear participante
- `GET /api/v1/participants/{id}` - Detalle de participante
- `PATCH /api/v1/participants/{id}` - Actualizar participante
- `DELETE /api/v1/participants/{id}` - Eliminar participante

## 🛠️ Configuración

### Cambiar URL de la API

Edita `js/config.js`:

```javascript
const API_CONFIG = {
    BASE_URL: 'http://localhost:5000/api/v1',  // Cambia esto
    TIMEOUT: 10000,
    RETRY_ATTEMPTS: 3
};
```

### Habilitar CORS en el Backend

Asegúrate de que el backend tenga CORS habilitado para la URL del frontend:

```bash
# En .env del backend
CORS_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

## 📱 Páginas Disponibles

### 1. Login (`#loginPage`)
- Formulario de autenticación
- Validación de campos
- Manejo de errores

### 2. Talleres (`#workshopsPage`)
- Grid de tarjetas de talleres
- Contador de participantes y sesiones
- Botón para crear nuevo taller

### 3. Detalle de Taller (`#workshopDetailPage`)
- Información completa del taller
- Lista de participantes
- Lista de sesiones
- Acciones: editar, eliminar

### 4. Perfil (`#profilePage`)
- Información del usuario actual
- Roles y permisos
- Estado de verificación

## 🎯 Funcionalidades Implementadas

### ✅ Completadas
- [x] Sistema de autenticación JWT
- [x] CRUD de talleres
- [x] CRUD de participantes
- [x] Navegación entre páginas
- [x] Modales reutilizables
- [x] Notificaciones toast
- [x] Manejo de errores
- [x] Diseño responsive
- [x] Refresh automático de tokens

### 🚧 Pendientes (Futuras)
- [ ] CRUD de sesiones
- [ ] Sistema de observaciones
- [ ] Búsqueda y filtros
- [ ] Paginación
- [ ] Exportar datos
- [ ] Modo oscuro
- [ ] Internacionalización (i18n)

## 🐛 Debugging

### Consola del Navegador

Abre las DevTools (F12) para ver:
- Errores de JavaScript
- Peticiones HTTP en la pestaña Network
- Estado de localStorage en Application

### Problemas Comunes

**Error: "Failed to fetch"**
- Verifica que el backend esté corriendo
- Revisa la URL en `config.js`
- Asegúrate de que CORS esté habilitado

**Error: "401 Unauthorized"**
- El token expiró o es inválido
- Intenta hacer logout y login nuevamente
- Verifica que `JWT_SECRET_KEY` sea el mismo en backend

**Error: "Network timeout"**
- El backend no responde
- Aumenta `TIMEOUT` en `config.js`
- Verifica la conexión de red

## 🔒 Seguridad

### Buenas Prácticas Implementadas

- ✅ Tokens JWT en localStorage (no cookies para evitar CSRF)
- ✅ Escape de HTML para prevenir XSS
- ✅ Validación de entrada en formularios
- ✅ HTTPS recomendado en producción
- ✅ Tokens con expiración

### Recomendaciones para Producción

1. **Usar HTTPS**: Siempre en producción
2. **Configurar CSP**: Content Security Policy headers
3. **Limitar CORS**: Solo dominios específicos
4. **Rate Limiting**: Implementar en el backend
5. **Monitoreo**: Logs de errores y actividad

## 📚 Recursos

- [Fetch API](https://developer.mozilla.org/es/docs/Web/API/Fetch_API)
- [LocalStorage](https://developer.mozilla.org/es/docs/Web/API/Window/localStorage)
- [JWT.io](https://jwt.io/) - Decodificar tokens
- [API Documentation](../.agent/docs/API.md) - Documentación completa de la API

## 🤝 Contribuir

Para agregar nuevas funcionalidades:

1. Crea un nuevo módulo en `js/` si es necesario
2. Sigue el patrón de los módulos existentes
3. Actualiza `app.js` con los event listeners
4. Mantén la consistencia de diseño con `styles.css`
5. Documenta cambios importantes

## 📄 Licencia

Este frontend es parte del proyecto Arteterapia.

---

**Desarrollado con ❤️ usando Vanilla JavaScript**
