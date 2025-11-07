# 🔐 Configuración de OAuth para YouTube Music

A partir de noviembre de 2024, YouTube Music requiere autenticación OAuth para funcionar correctamente.

## 📋 Pasos para configurar OAuth

### 1. Crear proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Dale un nombre como "Music Player App"

### 2. Habilitar YouTube Data API v3

1. En el menú lateral, ve a **"APIs y servicios"** > **"Biblioteca"**
2. Busca **"YouTube Data API v3"**
3. Haz clic en **"Habilitar"**

### 3. Crear credenciales OAuth 2.0

1. Ve a **"APIs y servicios"** > **"Credenciales"**
2. Haz clic en **"Crear credenciales"** > **"ID de cliente de OAuth"**
3. Si es la primera vez, configura la pantalla de consentimiento:
   - Tipo de usuario: **Externo**
   - Nombre de la aplicación: "Music Player"
   - Correo electrónico de asistencia: tu email
   - Dominios autorizados: (puedes dejarlo vacío)
   - Guarda los cambios

4. Vuelve a crear las credenciales:
   - Tipo de aplicación: **TVs y dispositivos con entrada limitada**
   - Nombre: "Music Player Client"
   - Haz clic en **"Crear"**

5. **Descarga el JSON** o copia el **Client ID** y **Client Secret**

### 4. Configurar en la aplicación

#### Opción A: Usar el script de configuración

```powershell
cd c:\Users\Cris\Desktop\music
C:/Users/Cris/Desktop/music/.venv/Scripts/python.exe setup_oauth.py
```

Ingresa tu `Client ID` y `Client Secret` cuando te lo pida.

#### Opción B: Configuración manual

Crea un archivo `oauth_config.env` en el directorio `music`:

```env
CLIENT_ID=tu_client_id_aqui.apps.googleusercontent.com
CLIENT_SECRET=tu_client_secret_aqui
```

### 5. Autorizar la aplicación

Ejecuta el comando de autenticación de ytmusicapi:

```powershell
cd c:\Users\Cris\Desktop\music
C:/Users/Cris/Desktop/music/.venv/Scripts/python.exe -m ytmusicapi oauth
```

Esto te mostrará:
1. Una URL para visitar
2. Un código para ingresar en esa URL

Sigue las instrucciones:
- Abre la URL en tu navegador
- Ingresa el código mostrado
- Inicia sesión con tu cuenta de Google
- Autoriza la aplicación

Esto creará un archivo `oauth.json` con tu token de acceso.

### 6. Reiniciar el servidor

```powershell
# Detén el servidor actual (Ctrl+C)
cd c:\Users\Cris\Desktop\music\backend
C:/Users/Cris/Desktop/music/.venv/Scripts/python.exe app.py
```

## ✅ Verificar que funciona

Deberías ver en la consola del servidor:

```
✅ Usando autenticación OAuth
 * Running on http://127.0.0.1:5000
```

## 🔧 Solución de problemas

### Error: "oauth.json no encontrado"
- Asegúrate de ejecutar `ytmusicapi oauth` en el directorio `music`
- El archivo debe estar en: `c:\Users\Cris\Desktop\music\oauth.json`

### Error: "client_id/client_secret no configurados"
- Verifica que `oauth_config.env` existe y tiene las credenciales correctas
- O configúralas como variables de entorno:
  ```powershell
  $env:CLIENT_ID="tu_client_id"
  $env:CLIENT_SECRET="tu_client_secret"
  ```

### Error al autorizar
- Verifica que has habilitado YouTube Data API v3
- Asegúrate de usar el tipo "TVs y dispositivos con entrada limitada"
- Intenta crear nuevas credenciales si persiste el error

## 📝 Archivos importantes

Después de la configuración, deberías tener:

```
music/
├── oauth.json              # Token de acceso (NO compartir)
├── oauth_config.env        # Credenciales OAuth (NO compartir)
├── setup_oauth.py          # Script de configuración
└── backend/
    └── app.py              # Servidor con soporte OAuth
```

## ⚠️ Seguridad

**NUNCA compartas estos archivos:**
- `oauth.json` - Contiene tu token de acceso
- `oauth_config.env` - Contiene tus credenciales OAuth

Estos archivos ya están incluidos en `.gitignore` para evitar subirlos accidentalmente.

## 🎵 Listo!

Una vez configurado OAuth, tu aplicación tendrá acceso completo a:
- Búsqueda de canciones
- Tu biblioteca personal
- Playlists
- Historial
- Y más funciones de YouTube Music
