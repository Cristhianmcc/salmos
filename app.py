from flask import Flask, jsonify, request, send_from_directory, Response, redirect
from flask_cors import CORS
from ytmusicapi import YTMusic
import os
import yt_dlp

app = Flask(__name__, static_folder='../frontend')
CORS(app)

# Inicializar YTMusic sin autenticación (modo público)
def init_ytmusic():
    print("🔓 Usando YouTube Music en modo público (sin autenticación)")
    print("   Esto permite búsquedas y reproducción básica")
    return YTMusic()

ytmusic = init_ytmusic()

@app.route('/')
def index():
    """Servir la página principal"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('../frontend/css', path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('../frontend/js', path)

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
    """Obtener URL de streaming para una canción usando yt-dlp"""
    try:
        # Construir URL de YouTube
        youtube_url = f'https://www.youtube.com/watch?v={video_id}'
        
        # Configuración de yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                
                # Buscar la mejor URL de audio
                if 'url' in info:
                    stream_url = info['url']
                elif 'formats' in info:
                    # Buscar el mejor formato de audio
                    audio_formats = [f for f in info['formats'] if f.get('acodec') != 'none']
                    if audio_formats:
                        best_audio = max(audio_formats, key=lambda f: f.get('abr', 0) or 0)
                        stream_url = best_audio['url']
                    else:
                        stream_url = info['formats'][-1]['url']
                else:
                    stream_url = None
                
                if stream_url:
                    return jsonify({
                        'videoId': video_id,
                        'streamUrl': stream_url,
                        'method': 'yt-dlp',
                        'title': info.get('title', ''),
                        'duration': info.get('duration', 0)
                    })
        except Exception as e:
            print(f"Error con yt-dlp: {e}")
        
        # Fallback: devolver URL de embed de YouTube
        return jsonify({
            'videoId': video_id,
            'embedUrl': f'https://www.youtube.com/embed/{video_id}',
            'method': 'embed'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
