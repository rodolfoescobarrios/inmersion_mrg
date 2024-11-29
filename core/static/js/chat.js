document.addEventListener("DOMContentLoaded", function () {
    const roomIdElement = document.getElementById("room_id");
    const userRoleElement = document.getElementById("user_role");

    if (!roomIdElement || !userRoleElement) {
        console.error("No se pudo encontrar el elemento room_id o user_role.");
        return;
    }

    const roomId = roomIdElement.value;
    const userRole = parseInt(userRoleElement.value, 10); // Convierte el rol a un entero

    console.log("Room ID:", roomId);
    console.log("User Role:", userRole);

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

        if (userRole !== 1) { // Solo verifica botones si el rol no es 1
            const btnMessage = document.getElementById("btnMessage");
            const inputMessage = document.getElementById("inputMessage");

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

            const playBtn = document.getElementById('playBtn');
            const pauseBtn = document.getElementById('pauseBtn');
            const seekBtn = document.getElementById('seekBtn');
            const restBtn = document.getElementById('restBtn'); // Nuevo botón para retroceder

            if (!playBtn || !pauseBtn || !seekBtn || !restBtn) {
                console.error("No se encontraron todos los botones de control del video.");
                return;
            }

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

            restBtn.onclick = function () {
                console.log("Botón Retroceder presionado");
                if (player) {
                    const time = Math.max(player.getCurrentTime() - 10, 0); // Retrocede 10 segundos, sin bajar de 0
                    sendControlAction('seek', time);
                }
            };
        }
    }
});
