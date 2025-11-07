// API Base URL
const API_URL = 'http://localhost:5000/api';

// Estado global
let currentPlayer = null;
let playerReady = false;
let isPlaying = false;
let currentVideoId = null;
let playlist = [];
let currentIndex = 0;

// Elementos del DOM
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const searchType = document.getElementById('searchType');
const searchResults = document.getElementById('searchResults');
const homeContent = document.getElementById('homeContent');
const chartsContent = document.getElementById('chartsContent');

const playBtn = document.getElementById('playBtn');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const progressBar = document.getElementById('progressBar');
const volumeBar = document.getElementById('volumeBar');
const muteBtn = document.getElementById('muteBtn');
const currentTime = document.getElementById('currentTime');
const duration = document.getElementById('duration');
const playerTitle = document.getElementById('playerTitle');
const playerArtist = document.getElementById('playerArtist');
const playerThumbnail = document.getElementById('playerThumbnail');

// Variables del player
let playerIframe = null;

// Funciones de historial y favoritos
function getHistory() {
    const history = localStorage.getItem('musicHistory');
    return history ? JSON.parse(history) : [];
}

function saveToHistory(song) {
    let history = getHistory();
    
    // Evitar duplicados - actualizar si ya existe
    history = history.filter(s => s.videoId !== song.videoId);
    
    // Agregar al inicio
    history.unshift({
        videoId: song.videoId,
        title: song.title,
        artist: song.artist,
        thumbnail: song.thumbnail,
        playedAt: new Date().toISOString()
    });
    
    // Mantener solo las últimas 50 canciones
    if (history.length > 50) {
        history = history.slice(0, 50);
    }
    
    localStorage.setItem('musicHistory', JSON.stringify(history));
}

function getLikedSongs() {
    const liked = localStorage.getItem('likedSongs');
    return liked ? JSON.parse(liked) : [];
}

function toggleLike(song) {
    let liked = getLikedSongs();
    const index = liked.findIndex(s => s.videoId === song.videoId);
    
    if (index > -1) {
        // Ya está en favoritos, remover
        liked.splice(index, 1);
        localStorage.setItem('likedSongs', JSON.stringify(liked));
        console.log('💔 Removido de favoritos');
        return false;
    } else {
        // Agregar a favoritos
        liked.unshift({
            videoId: song.videoId,
            title: song.title,
            artist: song.artist,
            thumbnail: song.thumbnail,
            likedAt: new Date().toISOString()
        });
        localStorage.setItem('likedSongs', JSON.stringify(liked));
        console.log('❤️ Agregado a favoritos');
        return true;
    }
}

function isLiked(videoId) {
    const liked = getLikedSongs();
    return liked.some(s => s.videoId === videoId);
}

// Inicializar cuando cargue la página
function initPlayerElements() {
    playerIframe = document.getElementById('ytPlayer');
    console.log('✅ Reproductor listo');
    
    // Cargar contenido de inicio automáticamente
    loadHome();
}

// Funciones de API
async function searchMusic(query, type = 'songs') {
    try {
        const response = await fetch(`${API_URL}/search?q=${encodeURIComponent(query)}&type=${type}&limit=20`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error en búsqueda:', error);
        return [];
    }
}

async function getHome() {
    try {
        const response = await fetch(`${API_URL}/home`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error obteniendo home:', error);
        return [];
    }
}

async function getCharts(country = 'US') {
    try {
        const response = await fetch(`${API_URL}/charts?country=${country}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error obteniendo charts:', error);
        return [];
    }
}

// Funciones de UI
function createSongCard(song) {
    const card = document.createElement('div');
    card.className = 'card';
    card.style.position = 'relative';
    
    const thumbnail = song.thumbnails ? song.thumbnails[0].url : '';
    const title = song.title || 'Sin título';
    const artists = song.artists ? song.artists.map(a => a.name).join(', ') : 'Artista desconocido';
    const duration = song.duration || '';
    const videoId = song.videoId || '';
    const liked = isLiked(videoId);
    
    card.innerHTML = `
        <img src="${thumbnail}" alt="${title}" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22200%22%3E%3Crect width=%22200%22 height=%22200%22 fill=%22%23282828%22/%3E%3Ctext x=%2250%25%22 y=%2250%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 fill=%22%23b3b3b3%22 font-size=%2220%22%3E🎵%3C/text%3E%3C/svg%3E'">
        <button class="like-btn" style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.7); border: none; border-radius: 50%; width: 35px; height: 35px; cursor: pointer; font-size: 18px; display: flex; align-items: center; justify-content: center; z-index: 10;">
            ${liked ? '❤️' : '🤍'}
        </button>
        <div class="card-title">${title}</div>
        <div class="card-subtitle">${artists}</div>
        <div class="card-info">${duration}</div>
    `;
    
    // Click en la tarjeta para reproducir
    card.addEventListener('click', (e) => {
        // No reproducir si se hizo click en el botón de like
        if (!e.target.classList.contains('like-btn')) {
            playSong(videoId, title, artists, thumbnail);
        }
    });
    
    // Click en el botón de like
    const likeBtn = card.querySelector('.like-btn');
    likeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isNowLiked = toggleLike({
            videoId,
            title,
            artist: artists,
            thumbnail
        });
        likeBtn.textContent = isNowLiked ? '❤️' : '🤍';
        
        // Recargar la sección activa para ver cambios en tiempo real
        const homeSection = document.getElementById('homeSection');
        const librarySection = document.getElementById('librarySection');
        
        if (homeSection && homeSection.classList.contains('active')) {
            loadHome();
        } else if (librarySection && librarySection.classList.contains('active')) {
            loadLibrary();
        }
    });
    
    return card;
}

function createAlbumCard(album) {
    const card = document.createElement('div');
    card.className = 'card';
    
    const thumbnail = album.thumbnails ? album.thumbnails[0].url : '';
    const title = album.title || 'Sin título';
    const artists = album.artists ? album.artists.map(a => a.name).join(', ') : '';
    const year = album.year || '';
    
    card.innerHTML = `
        <img src="${thumbnail}" alt="${title}">
        <div class="card-title">${title}</div>
        <div class="card-subtitle">${artists}</div>
        <div class="card-info">${year}</div>
    `;
    
    return card;
}

function createArtistCard(artist) {
    const card = document.createElement('div');
    card.className = 'card';
    
    const thumbnail = artist.thumbnails ? artist.thumbnails[0].url : '';
    const name = artist.artist || artist.name || 'Sin nombre';
    
    card.innerHTML = `
        <img src="${thumbnail}" alt="${name}" style="border-radius: 50%;">
        <div class="card-title">${name}</div>
        <div class="card-subtitle">Artista</div>
    `;
    
    return card;
}

// Funciones del reproductor - Abrir en YouTube Music
async function playSong(videoId, title, artist, thumbnail) {
    currentVideoId = videoId;
    playerTitle.textContent = title;
    playerArtist.textContent = artist;
    playerThumbnail.src = thumbnail;
    
    console.log('▶️ Cargando:', title);
    
    try {
        // Obtener URL de streaming desde el backend
        const response = await fetch(`${API_URL}/stream/${videoId}`);
        const data = await response.json();
        
        if (data.error) {
            console.error('❌ Error:', data.error);
            alert('No se pudo cargar la canción. Intenta con otra.');
            return;
        }
        
        // Crear o actualizar el elemento de audio
        let audioPlayer = document.getElementById('audioPlayer');
        if (!audioPlayer) {
            audioPlayer = document.createElement('audio');
            audioPlayer.id = 'audioPlayer';
            audioPlayer.controls = false;
            document.body.appendChild(audioPlayer);
        }
        
        // Establecer la fuente y reproducir
        audioPlayer.src = data.streamUrl || data.url;
        audioPlayer.play();
        
        isPlaying = true;
        playBtn.textContent = '⏸️';
        
        // Guardar en historial
        saveToHistory({
            videoId,
            title,
            artist,
            thumbnail
        });
        
        // Event listeners del audio
        audioPlayer.addEventListener('timeupdate', updateProgress);
        audioPlayer.addEventListener('ended', playNext);
        audioPlayer.addEventListener('loadedmetadata', () => {
            duration.textContent = formatTime(audioPlayer.duration);
        });
        
        console.log('✅ Reproduciendo:', title);
    } catch (error) {
        console.error('❌ Error reproduciendo:', error);
        alert('No se pudo reproducir la canción. Intenta con otra.');
    }
}

function updateProgress() {
    const audioPlayer = document.getElementById('audioPlayer');
    if (!audioPlayer) return;
    
    const progress = (audioPlayer.currentTime / audioPlayer.duration) * 100;
    progressBar.value = progress;
    currentTime.textContent = formatTime(audioPlayer.currentTime);
}

function togglePlay() {
    const audioPlayer = document.getElementById('audioPlayer');
    
    if (!audioPlayer || !currentVideoId) {
        console.warn('⚠️ No hay ninguna canción seleccionada');
        return;
    }
    
    if (isPlaying) {
        audioPlayer.pause();
        playBtn.textContent = '▶️';
        isPlaying = false;
        console.log('⏸️ Pausado');
    } else {
        audioPlayer.play();
        playBtn.textContent = '⏸️';
        isPlaying = true;
        console.log('▶️ Reproduciendo');
    }
}

function playNext() {
    if (playlist.length === 0) {
        console.warn('⚠️ No hay playlist cargada');
        return;
    }
    currentIndex = (currentIndex + 1) % playlist.length;
    const song = playlist[currentIndex];
    console.log('⏭️ Siguiente canción');
    playSong(song.videoId, song.title, song.artist, song.thumbnail);
}

function playPrev() {
    if (playlist.length === 0) {
        console.warn('⚠️ No hay playlist cargada');
        return;
    }
    currentIndex = (currentIndex - 1 + playlist.length) % playlist.length;
    const song = playlist[currentIndex];
    console.log('⏮️ Canción anterior');
    playSong(song.videoId, song.title, song.artist, song.thumbnail);
}

function startProgressTracking() {
    // El tracking se maneja con el evento timeupdate del audio player
}

function formatTime(seconds) {
    if (!seconds || isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Event Listeners
searchBtn.addEventListener('click', async () => {
    const query = searchInput.value.trim();
    if (!query) return;
    
    searchResults.innerHTML = '<p class="loading">Buscando</p>';
    showSection('search');
    
    try {
        const results = await searchMusic(query, searchType.value);
        
        searchResults.innerHTML = '';
        
        if (!results || !Array.isArray(results) || results.length === 0) {
            searchResults.innerHTML = '<p>No se encontraron resultados para "' + query + '"</p>';
            return;
        }
        
        playlist = [];
        results.forEach((item, index) => {
        let card;
        
        if (searchType.value === 'songs') {
            card = createSongCard(item);
            playlist.push({
                videoId: item.videoId,
                title: item.title,
                artist: item.artists ? item.artists.map(a => a.name).join(', ') : '',
                thumbnail: item.thumbnails ? item.thumbnails[0].url : ''
            });
        } else if (searchType.value === 'albums') {
            card = createAlbumCard(item);
        } else if (searchType.value === 'artists') {
            card = createArtistCard(item);
        } else {
            card = createSongCard(item);
        }
        
        searchResults.appendChild(card);
    });
    } catch (error) {
        console.error('Error en búsqueda:', error);
        searchResults.innerHTML = '<p>❌ Error al buscar. Intenta de nuevo.</p>';
    }
});

searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        searchBtn.click();
    }
});

playBtn.addEventListener('click', togglePlay);
nextBtn.addEventListener('click', playNext);
prevBtn.addEventListener('click', playPrev);

// Controles del reproductor
progressBar.addEventListener('input', (e) => {
    const audioPlayer = document.getElementById('audioPlayer');
    if (!audioPlayer) return;
    
    const time = (e.target.value / 100) * audioPlayer.duration;
    audioPlayer.currentTime = time;
});

volumeBar.addEventListener('input', (e) => {
    const audioPlayer = document.getElementById('audioPlayer');
    if (!audioPlayer) return;
    
    audioPlayer.volume = e.target.value / 100;
    
    // Actualizar ícono de mute
    if (audioPlayer.volume === 0) {
        muteBtn.textContent = '🔇';
    } else if (audioPlayer.volume < 0.5) {
        muteBtn.textContent = '🔉';
    } else {
        muteBtn.textContent = '🔊';
    }
});

muteBtn.addEventListener('click', () => {
    const audioPlayer = document.getElementById('audioPlayer');
    if (!audioPlayer) return;
    
    if (audioPlayer.volume > 0) {
        audioPlayer.dataset.previousVolume = audioPlayer.volume;
        audioPlayer.volume = 0;
        volumeBar.value = 0;
        muteBtn.textContent = '🔇';
    } else {
        const previousVolume = parseFloat(audioPlayer.dataset.previousVolume) || 0.5;
        audioPlayer.volume = previousVolume;
        volumeBar.value = previousVolume * 100;
        muteBtn.textContent = previousVolume < 0.5 ? '🔉' : '🔊';
    }
});

// Navegación
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', async (e) => {
        e.preventDefault();
        const section = link.dataset.section;
        
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        link.classList.add('active');
        
        showSection(section);
        
        // Cargar contenido según la sección
        if (section === 'home') {
            await loadHome();
        } else if (section === 'library') {
            await loadLibrary();
        } else if (section === 'charts' && chartsContent.innerHTML.includes('Cargando')) {
            await loadCharts();
        }
    });
});

function showSection(sectionName) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.getElementById(`${sectionName}Section`).classList.add('active');
}

async function loadHome() {
    homeContent.innerHTML = '<p class="loading">Cargando tu música...</p>';
    
    try {
        homeContent.innerHTML = '';
        
        const history = getHistory();
        const likedSongs = getLikedSongs();
        
        // Sección de canciones favoritas
        if (likedSongs.length > 0) {
            const likedSection = document.createElement('div');
            likedSection.style.marginBottom = '30px';
            
            const title = document.createElement('h3');
            title.innerHTML = '❤️ Tus canciones favoritas';
            title.style.marginBottom = '15px';
            likedSection.appendChild(title);
            
            const grid = document.createElement('div');
            grid.className = 'content-grid';
            
            likedSongs.slice(0, 12).forEach(song => {
                const card = createSongCard({
                    videoId: song.videoId,
                    title: song.title,
                    artists: [{ name: song.artist }],
                    thumbnails: [{ url: song.thumbnail }],
                    duration: ''
                });
                grid.appendChild(card);
            });
            
            likedSection.appendChild(grid);
            homeContent.appendChild(likedSection);
        }
        
        // Sección de reproducidos recientemente
        if (history.length > 0) {
            const historySection = document.createElement('div');
            historySection.style.marginBottom = '30px';
            
            const title = document.createElement('h3');
            title.innerHTML = '🕐 Reproducidos recientemente';
            title.style.marginBottom = '15px';
            historySection.appendChild(title);
            
            const grid = document.createElement('div');
            grid.className = 'content-grid';
            
            history.slice(0, 12).forEach(song => {
                const card = createSongCard({
                    videoId: song.videoId,
                    title: song.title,
                    artists: [{ name: song.artist }],
                    thumbnails: [{ url: song.thumbnail }],
                    duration: ''
                });
                grid.appendChild(card);
            });
            
            historySection.appendChild(grid);
            homeContent.appendChild(historySection);
        }
        
        // Si no hay nada
        if (history.length === 0 && likedSongs.length === 0) {
            homeContent.innerHTML = `
                <div style="text-align: center; padding: 50px; color: #b3b3b3;">
                    <h2 style="font-size: 48px; margin-bottom: 20px;">🎵</h2>
                    <h3 style="margin-bottom: 10px;">Comienza a escuchar música</h3>
                    <p>Usa la búsqueda para encontrar tus canciones favoritas</p>
                    <p style="margin-top: 20px;">Las canciones que reproduzcas aparecerán aquí</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error cargando home:', error);
        homeContent.innerHTML = '<p>⚠️ Error al cargar el contenido. Intenta recargar la página.</p>';
    }
}

async function loadCharts() {
    chartsContent.innerHTML = '<p class="loading">Cargando charts</p>';
    const chartsData = await getCharts();
    
    chartsContent.innerHTML = '';
    
    if (chartsData && chartsData.length > 0) {
        chartsData.forEach(chart => {
            if (chart.items) {
                const chartDiv = document.createElement('div');
                chartDiv.style.marginBottom = '30px';
                
                const title = document.createElement('h3');
                title.textContent = chart.title || 'Top Songs';
                title.style.marginBottom = '15px';
                chartDiv.appendChild(title);
                
                const grid = document.createElement('div');
                grid.className = 'content-grid';
                
                chart.items.slice(0, 10).forEach(item => {
                    const card = createSongCard(item);
                    grid.appendChild(card);
                });
                
                chartDiv.appendChild(grid);
                chartsContent.appendChild(chartDiv);
            }
        });
    } else {
        chartsContent.innerHTML = '<p>No hay charts disponibles</p>';
    }
}

async function loadLibrary() {
    const libraryContent = document.getElementById('libraryContent');
    libraryContent.innerHTML = '<p class="loading">Cargando tu biblioteca...</p>';
    
    try {
        const likedSongs = getLikedSongs();
        libraryContent.innerHTML = '';
        
        if (likedSongs.length > 0) {
            const grid = document.createElement('div');
            grid.className = 'content-grid';
            
            likedSongs.forEach(song => {
                const card = createSongCard({
                    videoId: song.videoId,
                    title: song.title,
                    artists: [{ name: song.artist }],
                    thumbnails: [{ url: song.thumbnail }],
                    duration: ''
                });
                grid.appendChild(card);
            });
            
            libraryContent.appendChild(grid);
        } else {
            libraryContent.innerHTML = `
                <div style="text-align: center; padding: 50px; color: #b3b3b3;">
                    <h2 style="font-size: 48px; margin-bottom: 20px;">❤️</h2>
                    <h3 style="margin-bottom: 10px;">Tu biblioteca está vacía</h3>
                    <p>Marca canciones como favoritas para verlas aquí</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error cargando biblioteca:', error);
        libraryContent.innerHTML = '<p>⚠️ Error al cargar la biblioteca.</p>';
    }
}

// Cargar contenido inicial
window.addEventListener('load', async () => {
    console.log('✅ Página cargada');
    initPlayerElements();
    await loadHome();
});
