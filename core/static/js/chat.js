function loadYouTubeAPI() {
    if (typeof YT === 'undefined' || typeof YT.Player === 'undefined') {
        const tag = document.createElement('script');
        tag.src = "https://www.youtube.com/iframe_api";
        const firstScriptTag = document.getElementsByTagName('script')[0];
        firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
    }
}

loadYouTubeAPI();
document.addEventListener("DOMContentLoaded", function () {
    const roomIdElement = document.getElementById("room_id");
    if (!roomIdElement) {
        console.error("No se pudo encontrar el elemento room_id.");
        return;
    }

    const roomId = roomIdElement.value;
    console.log("Room ID:", roomId);

    if (roomId) {
        const socket = new WebSocket(`wss://${window.location.host}/ws/room/${roomId}/`);

        let player; // Variable global para el reproductor de YouTube

        socket.onopen = function () {
            console.log("WebSocket conectado.");
        };

        socket.onmessage = function (e) {
            const data = JSON.parse(e.data);
            console.log("Mensaje recibido:", data);

            // Cargar video si contiene un enlace de YouTube
            if (data.message && data.message.includes("https://www.youtube.com/watch")) {
                const videoId = extractVideoId(data.message);
                if (videoId) {
                    loadVideo(videoId); // Cargar el video recibido
                }
            }

            // Manejar acciones del video (reproducir, pausar, adelantar)
            if (data.action) {
                handleVideoAction(data.action, data.time);
            }
        };

        socket.onclose = function (e) {
            console.error("WebSocket cerrado:", e);
        };

        socket.onerror = function (e) {
            console.error("Error en WebSocket:", e);
        };

        const btnMessage = document.getElementById("btnMessage");
        const inputMessage = document.getElementById("inputMessage");

        // Verificar que los elementos existan
        if (!btnMessage || !inputMessage) {
            console.error("No se encontraron los elementos del formulario de mensaje.");
            return;
        }

        btnMessage.onclick = function () {
            const message = inputMessage.value.trim();
            if (message) {
                socket.send(JSON.stringify({ message: message }));
                inputMessage.value = '';
            } else {
                console.error("No hay mensaje para enviar.");
            }
        };

        // Función para extraer el ID de un video de YouTube
        function extractVideoId(url) {
            const match = url.match(/(?:https?:\/\/(?:www\.)?youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
            return match ? match[1] : null;
        }

        // Función para cargar el video en el reproductor de YouTube
        function loadVideo(videoId) {
            if (!player) {
                // Si el reproductor no ha sido creado, crea uno
                player = new YT.Player('video-player', {
                    height: '390',
                    width: '640',
                    videoId: videoId,
                    playerVars: {
                        'autohide': 1,
                        'rel': 0,
                        'fs': 1,
                        'modestbranding': 1,
                        'enablejsapi': 1,
                        'showinfo': 0,
                        'iv_load_policy': 3,
                        'playsinline': 1,
                        'origin': window.location.origin, // Indica el origen permitido para evitar problemas de CORS
                        'widget_referrer': window.location.href,
                        'vr_mode': 1,
                        'mute': 0,
                    },
                    events: {
                        'onReady': onPlayerReady,
                        'onError': onPlayerError
                    }
                });

            } else {
                // Si el reproductor ya existe, solo carga el nuevo video
                player.loadVideoById(videoId);
            }
        }

        function onPlayerReady(event) {
            console.log("Player listo. Reproduciendo video automáticamente.");
            event.target.unMute(); // Desactivar mute explícitamente
            event.target.playVideo();  // Reproduce el video automáticamente cuando esté listo

            // Habilitar los botones de control
            if (playBtn && pauseBtn && seekBtn) {
                playBtn.disabled = false;
                pauseBtn.disabled = false;
                seekBtn.disabled = false;
            }
        }

        function onPlayerError(event) {
            console.error("Error en el reproductor de YouTube:", event.data);
        }

        // Función para manejar las acciones de reproducción de video
        function handleVideoAction(action, time) {
            if (!player || typeof player.getPlayerState !== 'function') {
                console.error("El reproductor aún no está listo para recibir acciones.");
                return;
            }

            const playerState = player.getPlayerState();
            if (playerState === -1 || playerState === 3) {
                console.warn("El reproductor está en estado de no estar listo (-1) o está cargando (3). Acción no se ejecutará ahora.");
                return;
            }

            console.log("Acción recibida:", action, "Tiempo:", time);
            if (time && isNaN(time)) {
                console.error("Tiempo no válido:", time);
                return;
            }

            switch (action) {
                case 'play':
                    player.playVideo();
                    break;
                case 'pause':
                    player.pauseVideo();
                    break;
                case 'seek':
                    if (time !== null) {
                        player.seekTo(time, true);
                    }
                    break;
                default:
                    console.error("Acción desconocida:", action);
            }
        }


        // Función para enviar las acciones de control del video
        function sendControlAction(action, time = null) {
            if (socket.readyState === WebSocket.OPEN) {
                const message = { action: action };
                if (action === 'seek' && time !== null && !isNaN(time)) {
                    message.time = time;
                }

                const messageString = JSON.stringify(message);
                console.log("Enviando acción:", messageString);
                try {
                    socket.send(messageString);
                } catch (error) {
                    console.error("Error al enviar el mensaje:", error);
                }
            } else {
                console.error("WebSocket no está abierto. Estado:", socket.readyState);
            }
        }



        // Verificar que los botones de control existan
        const playBtn = document.getElementById('playBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        const seekBtn = document.getElementById('seekBtn');
        const restBtn = document.getElementById('restBtn'); // Nuevo botón para retroceder

        if (!playBtn || !pauseBtn || !seekBtn || !restBtn) {
            console.error("No se encontraron todos los botones de control del video.");
            return;
        }

        // Añadir eventos a los botones de control del video
        playBtn.onclick = function () {
            console.log("Botón Play presionado");
            if (player) {
                sendControlAction('play', player.getCurrentTime());
            }
        };

        pauseBtn.onclick = function () {
            console.log("Botón Pause presionado");
            if (player) {
                sendControlAction('pause', player.getCurrentTime());
            }
        };

        seekBtn.onclick = function () {
            console.log("Botón Seek presionado");
            if (player) {
                const time = player.getCurrentTime() + 10; // Adelanta 30 segundos
                sendControlAction('seek', time);
            }
        };

        // Nuevo evento para retroceder 10 segundos
        restBtn.onclick = function () {
            console.log("Botón Retroceder presionado");
            if (player) {
                const time = Math.max(player.getCurrentTime() - 10, 0); // Retrocede 10 segundos, sin bajar de 0
                sendControlAction('seek', time);
            }
        }
    };


        // Asegurarse de que la API de YouTube esté cargada antes de crear el reproductor
        function loadYouTubeAPI() {
            if (typeof YT === 'undefined' || typeof YT.Player === 'undefined') {
                const tag = document.createElement('script');
                tag.src = "https://www.youtube.com/iframe_api";
                const firstScriptTag = document.getElementsByTagName('script')[0];
                firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
            }
        }

        loadYouTubeAPI();
    });