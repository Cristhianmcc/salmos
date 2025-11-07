# 🎵 Music Player - Alternativa a YouTube Music

Una aplicación web de reproducción de música que utiliza la API de YouTube Music a través de `ytmusicapi` para ofrecer una experiencia similar a YouTube Music.

## 🚀 Características

- 🔍 Búsqueda de canciones, artistas, álbumes y playlists
- ▶️ Reproductor de música integrado con controles completos
- 📊 Visualización de charts y tendencias
- 🏠 Página de inicio con recomendaciones
- 🎨 Interfaz moderna y responsive inspirada en Spotify
- 📱 Compatible con dispositivos móviles

## 📋 Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Navegador web moderno (Chrome, Firefox, Edge, Safari)

## 🔧 Instalación

### 1. Clonar o descargar el proyecto

```bash
cd c:\Users\Cris\Desktop\music
```

### 2. Crear un entorno virtual (recomendado)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```powershell
pip install -r requirements.txt
```

## 🎮 Uso

### Iniciar el servidor

```powershell
cd backend
python app.py
```

El servidor se iniciará en `http://localhost:5000`

### Acceder a la aplicación

Abre tu navegador y visita: `http://localhost:5000`

## 📁 Estructura del Proyecto

```
music/
├── backend/
│   └── app.py              # Servidor Flask con API REST
├── frontend/
│   ├── index.html          # Página principal
│   ├── css/
│   │   └── styles.css      # Estilos de la aplicación
│   └── js/
│       └── app.js          # Lógica del frontend
├── requirements.txt        # Dependencias de Python
└── README.md              # Este archivo
```

## 🛠️ API Endpoints

### Búsqueda
- `GET /api/search?q=query&type=songs&limit=20`
  - Tipos: `songs`, `albums`, `artists`, `playlists`

### Contenido
- `GET /api/home` - Página de inicio con recomendaciones
- `GET /api/charts?country=US` - Charts por país

### Detalles
- `GET /api/song/<video_id>` - Información de una canción
- `GET /api/artist/<browse_id>` - Información de un artista
- `GET /api/album/<browse_id>` - Información de un álbum
- `GET /api/playlist/<playlist_id>` - Canciones de una playlist

### Letras
- `GET /api/lyrics/<browse_id>` - Letras de una canción

## 🎵 Cómo Funciona

1. **Backend (Flask + ytmusicapi)**:
   - Servidor Python que actúa como intermediario
   - Consume la API de YouTube Music usando `ytmusicapi`
   - Expone endpoints REST para el frontend

2. **Frontend (HTML/CSS/JavaScript)**:
   - Interfaz de usuario moderna y responsive
   - Utiliza YouTube IFrame API para reproducir videos
   - Consume los endpoints del backend para obtener datos

3. **Reproducción**:
   - Las canciones se reproducen usando el YouTube IFrame Player API
   - El audio proviene directamente de YouTube
   - Controles de reproducción personalizados

## ⚠️ Limitaciones y Notas

1. **Streaming de Audio**: 
   - La reproducción usa la API de YouTube IFrame, que reproduce el video completo
   - Para streaming solo de audio, considera integrar `yt-dlp`

2. **Autenticación**:
   - Esta versión usa `ytmusicapi` sin autenticación
   - Para acceder a tu biblioteca personal, necesitarás autenticarte

3. **Rate Limiting**:
   - YouTube puede limitar las peticiones si son excesivas
   - Considera implementar caché para reducir llamadas a la API

## 🔐 Autenticación Opcional

Para acceder a tu biblioteca personal de YouTube Music:

```python
# En backend/app.py, reemplaza:
ytmusic = YTMusic()

# Por:
ytmusic = YTMusic('oauth.json')
```

Luego genera el archivo `oauth.json`:

```bash
ytmusicapi oauth
```

## 🚀 Mejoras Futuras

- [ ] Implementar playlists personalizadas
- [ ] Sistema de favoritos local
- [ ] Historial de reproducción
- [ ] Cola de reproducción editable
- [ ] Modo oscuro/claro
- [ ] Descarga de canciones (con permisos apropiados)
- [ ] Integración con yt-dlp para streaming solo de audio
- [ ] Cache de resultados
- [ ] Búsqueda por voz

## 📝 Tecnologías Utilizadas

- **Backend**: Python, Flask, ytmusicapi, flask-cors
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Reproducción**: YouTube IFrame API

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## ⚖️ Licencia

Este proyecto es para uso educativo. Respeta los términos de servicio de YouTube y las leyes de derechos de autor.

## 📧 Contacto

Para preguntas o sugerencias, abre un issue en el repositorio.

## 🙏 Agradecimientos

- [ytmusicapi](https://github.com/sigma67/ytmusicapi) por la excelente librería
- YouTube Music por la API no oficial
- La comunidad de código abierto

---

**Nota**: Esta aplicación es un proyecto educativo y no está afiliada con YouTube o Google.
