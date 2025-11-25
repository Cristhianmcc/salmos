from flask import Flask, jsonify, request, send_from_directory, Response, redirect
from flask_cors import CORS
from ytmusicapi import YTMusic
import os
import yt_dlp
import requests

app = Flask(__name__)
CORS(app)

# Obtener la ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

# Inicializar YTMusic sin autenticación (modo público )
def init_ytmusic():
    print("🔓 Usando YouTube Music en modo público (sin autenticación)")
    print("   Esto permite búsquedas y reproducción básica")
    return YTMusic()

ytmusic = init_ytmusic()

@app.route('/')
def index():
    """Servir la página principal"""
    print(f"📂 FRONTEND_DIR: {FRONTEND_DIR}")
    print(f"📄 Buscando: {os.path.join(FRONTEND_DIR, 'index.html')}")
    print(f"✅ Existe: {os.path.exists(os.path.join(FRONTEND_DIR, 'index.html'))}")
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'css'), path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'js'), path)

@app.route('/api/search', methods=['GET'])
def search():
    """Buscar canciones, artistas, álbumes"""
    try:
        query = request.args.get('q', '')
        filter_type = request.args.get('type', 'songs')  # songs, albums, artists, playlists
        limit = int(request.args.get('limit', 20))
        
        if not query:
            return jsonify([]), 200
        
        print(f"🔍 Buscando: '{query}' tipo: {filter_type}")
        results = ytmusic.search(query, filter=filter_type, limit=limit)
        print(f"✅ Encontrados {len(results) if results else 0} resultados")
        
        # Asegurar que siempre devolvemos una lista
        if not results:
            return jsonify([]), 200
        
        return jsonify(results), 200
    except Exception as e:
        print(f"❌ Error en búsqueda: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        # Devolver lista vacía en caso de error para no romper el frontend
        return jsonify([]), 200

@app.route('/api/song/<video_id>', methods=['GET'])
def get_song(video_id):
    """Obtener información detallada de una canción"""
    try:
        song = ytmusic.get_song(video_id)
        return jsonify(song)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stream/<video_id>', methods=['GET'])
def get_stream_url(video_id):
    """Obtener URL de streaming usando yt-dlp con configuración mejorada"""
    try:
        youtube_url = f'https://www.youtube.com/watch?v={video_id}'
        
        # Configuración mejorada de yt-dlp para evitar detección de bot
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'geo_bypass': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                
                # Buscar la mejor URL de audio
                stream_url = None
                if 'url' in info:
                    stream_url = info['url']
                elif 'formats' in info:
                    # Buscar formato de audio específico (140 = m4a audio 128k)
                    audio_formats = [f for f in info['formats'] 
                                   if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
                    if audio_formats:
                        # Preferir formato 140 (m4a 128k) o el de mejor calidad
                        best_audio = max(audio_formats, key=lambda f: f.get('abr', 0) or 0)
                        stream_url = best_audio.get('url')
                
                if stream_url:
                    print(f"✅ Stream directo obtenido para {video_id}")
                    return jsonify({
                        'videoId': video_id,
                        'streamUrl': stream_url,
                        'method': 'direct',
                        'title': info.get('title', ''),
                        'duration': info.get('duration', 0)
                    })
                    
        except Exception as e:
            error_msg = str(e)
            print(f"⚠️ Error con yt-dlp: {error_msg}")
            
            # Si YouTube pide autenticación, usar URL de embed directamente
            if 'Sign in' in error_msg or 'bot' in error_msg:
                print(f"🔒 YouTube bloqueó el acceso, usando embed para {video_id}")
                return jsonify({
                    'videoId': video_id,
                    'embedUrl': f'https://www.youtube.com/watch?v={video_id}',
                    'method': 'embed',
                    'message': 'YouTube requiere abrir en navegador'
                })
        
        # Fallback final: URL de YouTube directo
        print(f"📺 Usando URL de YouTube directo para {video_id}")
        return jsonify({
            'videoId': video_id,
            'embedUrl': f'https://www.youtube.com/watch?v={video_id}',
            'method': 'youtube'
        })
        
    except Exception as e:
        print(f"❌ Error general en stream: {e}")
        return jsonify({
            'videoId': video_id,
            'embedUrl': f'https://www.youtube.com/watch?v={video_id}',
            'method': 'fallback'
        }), 200
        
    except Exception as e:
        print(f"❌ Error en stream: {e}")
        # Fallback final: embed de YouTube
        return jsonify({
            'videoId': video_id,
            'embedUrl': f'https://www.youtube.com/embed/{video_id}',
            'method': 'embed'
        })

@app.route('/api/artist/<browse_id>', methods=['GET'])
def get_artist(browse_id):
    """Obtener información de un artista"""
    try:
        artist = ytmusic.get_artist(browse_id)
        return jsonify(artist)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/album/<browse_id>', methods=['GET'])
def get_album(browse_id):
    """Obtener información de un álbum"""
    try:
        album = ytmusic.get_album(browse_id)
        return jsonify(album)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/playlist/<playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    """Obtener canciones de una playlist"""
    try:
        limit = int(request.args.get('limit', 100))
        playlist = ytmusic.get_playlist(playlist_id, limit=limit)
        return jsonify(playlist)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/home', methods=['GET'])
def get_home():
    """Obtener contenido de la página de inicio (recomendaciones)"""
    # Temporalmente deshabilitado - YouTube Music API está rechazando esta petición
    # La búsqueda funciona perfectamente
    print("ℹ️ Home temporalmente deshabilitado - usa la búsqueda")
    return jsonify([]), 200

@app.route('/api/charts', methods=['GET'])
def get_charts():
    """Obtener los charts/rankings"""
    try:
        country = request.args.get('country', 'US')
        charts = ytmusic.get_charts(country=country)
        return jsonify(charts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lyrics/<browse_id>', methods=['GET'])
def get_lyrics(browse_id):
    """Obtener letras de una canción"""
    try:
        lyrics = ytmusic.get_lyrics(browse_id)
        return jsonify(lyrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cover/search', methods=['GET'])
def search_cover():
    """Buscar carátula HD usando iTunes API"""
    query = request.args.get('q', '')
    
    print(f"🎨 Buscando cover para: {query}")
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    try:
        # Usar iTunes Search API (no requiere API key y da excelentes resultados)
        response = requests.get(
            'https://itunes.apple.com/search',
            params={
                'term': query,
                'media': 'music',
                'entity': 'song',
                'limit': 1
            },
            timeout=8
        )
        data = response.json()
        
        print(f"📊 iTunes response: {data.get('resultCount', 0)} resultados")
        
        if data.get('results') and len(data['results']) > 0:
            result = data['results'][0]
            artwork_url = result.get('artworkUrl100', '')
            
            # iTunes devuelve artwork de 100x100 pero podemos solicitar tamaños más grandes
            # Reemplazando '100x100' con dimensiones más grandes en la URL
            cover_data = {
                'cover_small': artwork_url.replace('100x100', '200x200'),
                'cover_medium': artwork_url.replace('100x100', '400x400'),
                'cover_big': artwork_url.replace('100x100', '600x600'),
                'cover_xl': artwork_url.replace('100x100', '1200x1200'),  # iTunes soporta hasta 1200x1200
                'title': result.get('trackName'),
                'artist': result.get('artistName'),
                'album': result.get('collectionName')
            }
            
            print(f"✅ Cover encontrado: {cover_data['cover_xl']}")
            print(f"   Artista: {cover_data['artist']}, Canción: {cover_data['title']}")
            return jsonify(cover_data)
        
        print(f"⚠️  No se encontró cover para: {query}")
        return jsonify({'error': 'No cover found'}), 404
    except Exception as e:
        print(f"❌ Error fetching cover: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/lyrics/search', methods=['GET'])
def search_lyrics():
    """Buscar letras usando YTMusic (primario) o Lyrics.ovh (fallback)"""
    video_id = request.args.get('videoId')
    artist = request.args.get('artist', '')
    title = request.args.get('title', '')
    
    print(f"🎤 Buscando letras. VideoID: {video_id}, Artista: {artist}, Título: {title}")
    
    # 1. Intentar con YouTube Music si tenemos videoId
    if video_id:
        try:
            print(f"🎵 Intentando obtener letras de YTMusic para {video_id}...")
            watch_playlist = ytmusic.get_watch_playlist(videoId=video_id)
            
            if watch_playlist and 'lyrics' in watch_playlist and watch_playlist['lyrics']:
                lyrics_id = watch_playlist['lyrics']
                print(f"� Lyrics ID encontrado: {lyrics_id}")
                
                lyrics_data = ytmusic.get_lyrics(lyrics_id)
                if lyrics_data and 'lyrics' in lyrics_data:
                    print("✅ Letras encontradas en YTMusic")
                    return jsonify({
                        'lyrics': lyrics_data['lyrics'],
                        'source': 'ytmusic'
                    })
            print("⚠️ No se encontraron letras en YTMusic")
        except Exception as e:
            print(f"❌ Error con YTMusic lyrics: {e}")

    # 2. Fallback a Lyrics.ovh
    if artist and title:
        try:
            print(f"🌍 Intentando fallback con Lyrics.ovh para {artist} - {title}")
            url = f'https://api.lyrics.ovh/v1/{artist}/{title}'
            response = requests.get(url, timeout=5) # Timeout reducido para no bloquear
            
            if response.ok:
                data = response.json()
                lyrics_text = data.get('lyrics', '')
                if lyrics_text:
                    print("✅ Letras encontradas en Lyrics.ovh")
                    return jsonify({
                        'lyrics': lyrics_text,
                        'source': 'lyrics.ovh'
                    })
        except Exception as e:
            print(f"❌ Error con Lyrics.ovh: {e}")

    return jsonify({'error': 'Lyrics not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
