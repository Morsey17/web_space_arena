class GameClient {
    constructor() {
        this.socket = io();
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.gameState = null;
        this.playerId = null;
        this.keys = {};
        this.mouse = { x: 0, y: 0, isDown: false };

        this.init();
    }

    init() {
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());

        // Настройка обработчиков событий
        this.setupEventListeners();

        // Подключение к серверу
        this.setupSocketIO();

        // Запуск игрового цикла
        this.gameLoop();
    }

    resizeCanvas() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    setupEventListeners() {
        // Клавиатура
        window.addEventListener('keydown', (e) => {
            e.preventDefault(); // Предотвращаем поведение по умолчанию
            const key = e.key.toLowerCase();
            this.keys[key] = true;

            if (key === 'a' || key === 'd' || key === 'arrowleft' || key === 'arrowright') {
                const action = (key === 'a' || key === 'arrowleft') ? 'move_left' : 'move_right';
                console.log(`Нажата клавиша: ${key}, действие: ${action}`);
                this.sendPlayerAction(action, true);
            }
        });

        window.addEventListener('keyup', (e) => {
            const key = e.key.toLowerCase();
            this.keys[key] = false;

            if (key === 'a' || key === 'd' || key === 'arrowleft' || key === 'arrowright') {
                const action = (key === 'a' || key === 'arrowleft') ? 'move_left' : 'move_right';
                this.sendPlayerAction(action, false);
            }
        });

        // Мышь
        this.canvas.addEventListener('mousemove', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            this.mouse.x = e.clientX - rect.left;
            this.mouse.y = e.clientY - rect.top;

            this.sendPlayerAction('mouse_move', {
                x: this.mouse.x,
                y: this.mouse.y
            });
        });

        this.canvas.addEventListener('mousedown', (e) => {
            if (e.button === 0) {
                this.mouse.isDown = true;
                console.log('Мышь нажата');
                this.sendPlayerAction('mouse_down', true);
            }
        });

        this.canvas.addEventListener('mouseup', (e) => {
            if (e.button === 0) {
                this.mouse.isDown = false;
                this.sendPlayerAction('mouse_down', false);
            }
        });

        // Тач-события для мобильных устройств
        this.canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            if (e.touches.length > 0) {
                const touch = e.touches[0];
                const rect = this.canvas.getBoundingClientRect();
                this.mouse.x = touch.clientX - rect.left;
                this.mouse.y = touch.clientY - rect.top;
                this.mouse.isDown = true;
                this.sendPlayerAction('mouse_down', true);
                this.sendPlayerAction('mouse_move', { x: this.mouse.x, y: this.mouse.y });
            }
        });

        this.canvas.addEventListener('touchmove', (e) => {
            e.preventDefault();
            if (e.touches.length > 0) {
                const touch = e.touches[0];
                const rect = this.canvas.getBoundingClientRect();
                this.mouse.x = touch.clientX - rect.left;
                this.mouse.y = touch.clientY - rect.top;
                this.sendPlayerAction('mouse_move', { x: this.mouse.x, y: this.mouse.y });
            }
        });

        this.canvas.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.mouse.isDown = false;
            this.sendPlayerAction('mouse_down', false);
        });

        this.canvas.addEventListener('click', () => {
            this.canvas.focus();
        });

        // Устанавливаем атрибут tabindex для canvas
        this.canvas.setAttribute('tabindex', '1');
    }

    setupSocketIO() {
        this.socket.on('connect', () => {
            console.log('Подключено к серверу игры');
            this.playerId = this.socket.id;
            this.updateConnectionStatus(true);
        });

        this.socket.on('connected', (data) => {
            console.log(data.message);
        });

        this.socket.on('game_update', (gameState) => {
            this.gameState = gameState;
            this.updateUI(gameState);
        });

        this.socket.on('disconnect', () => {
            console.log('Отключено от сервера');
            this.updateConnectionStatus(false);
        });

        this.socket.on('connect_error', (error) => {
            console.error('Ошибка подключения:', error);
            this.updateConnectionStatus(false);
        });
    }

    updateConnectionStatus(isConnected) {
        const statusEl = document.getElementById('connectionStatus');
        if (statusEl) {
            if (isConnected) {
                statusEl.textContent = 'Подключено ✓';
                statusEl.classList.remove('disconnected');
            } else {
                statusEl.textContent = 'Нет подключения ✗';
                statusEl.classList.add('disconnected');
            }
        }
    }

    sendPlayerAction(action, value) {
        if (this.socket.connected) {
            this.socket.emit('player_action', {
                action: action,
                value: value
            });
        } else {
            console.warn('Не удалось отправить действие: нет подключения');
        }
    }

    updateUI(gameState) {
        // Обновление статистики
        if (gameState.players && this.playerId && gameState.players[this.playerId]) {
            const player = gameState.players[this.playerId];

            document.getElementById('playerHealth').textContent = Math.ceil(player.health);
            document.getElementById('playerStatus').textContent =
                player.is_respawning ? 'Возрождение...' : 'В бою';
            document.getElementById('respawnTime').textContent =
                player.is_respawning ? Math.ceil(player.respawn_timer / 1000) : '-';
        }

        // Подсчет объектов по командам
        if (gameState.titans && gameState.towers && gameState.drones) {
            const redTitans = gameState.titans.filter(t => t.team === 'red').length;
            const blueTitans = gameState.titans.filter(t => t.team === 'blue').length;
            const redTowers = gameState.towers.filter(t => t.team === 'red').length;
            const blueTowers = gameState.towers.filter(t => t.team === 'blue').length;
            const redDrones = gameState.drones.filter(d => d.team === 'red').length;
            const blueDrones = gameState.drones.filter(d => d.team === 'blue').length;

            document.getElementById('redTowers').textContent = redTowers;
            document.getElementById('blueTowers').textContent = blueTowers;
            document.getElementById('redDrones').textContent = redDrones;
            document.getElementById('blueDrones').textContent = blueDrones;
        }

        document.getElementById('gameTime').textContent = Math.floor(gameState.game_time / 1000);
    }

    gameLoop() {
        // Очистка canvas
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Отрисовка игры, если есть состояние
        if (this.gameState) {
            this.drawGame();
        }

        requestAnimationFrame(() => this.gameLoop());
    }

    drawGame() {
        // В этой упрощенной версии просто рисуем объекты по их координатам
        // В реальной игре нужно добавить камеру, масштабирование и т.д.
    
        // Масштаб для отображения
        const scale = 1;
        
        // Получаем данные текущего игрока
        let player = null;
        if (this.playerId && this.gameState.players[this.playerId]) {
            player = this.gameState.players[this.playerId];
        }
    
        // Центр экрана
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
    
        // Если есть игрок, центрируем камеру на нем
        let cameraX = 0;
        let cameraY = 0;
        
        if (player) {
            cameraX = player.position.x;
            cameraY = player.position.y;
        }
    
        // Очистка canvas с звездным фоном
        this.drawBackground();
    
        // Отрисовка объектов
        this.drawObjects(this.gameState.titans, cameraX, cameraY, centerX, centerY, scale);
        this.drawObjects(this.gameState.towers, cameraX, cameraY, centerX, centerY, scale);
        this.drawDrones(this.gameState.drones, cameraX, cameraY, centerX, centerY, scale);
        this.drawObjects(this.gameState.bullets, cameraX, cameraY, centerX, centerY, scale);
        this.drawObjects(this.gameState.missiles, cameraX, cameraY, centerX, centerY, scale);
        this.drawObjects(this.gameState.explosions, cameraX, cameraY, centerX, centerY, scale);
    
        // Отрисовка игроков
        for (const playerId in this.gameState.players) {
            const p = this.gameState.players[playerId];
            this.drawPlayer(p, cameraX, cameraY, centerX, centerY, playerId === this.playerId);
        }
    }

    drawBackground() {
        // Рисуем звездное небо
        const gradient = this.ctx.createRadialGradient(
            this.canvas.width / 2, this.canvas.height / 2, 0,
            this.canvas.width / 2, this.canvas.height / 2, this.canvas.width / 2
        );
        gradient.addColorStop(0, '#0a0a2a');
        gradient.addColorStop(1, '#000');
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Рисуем звезды (просто для вида)
        this.ctx.fillStyle = 'white';
        for (let i = 0; i < 50; i++) {
            const x = (i * 12345) % this.canvas.width;
            const y = (i * 6789) % this.canvas.height;
            const size = Math.random() * 2;
            this.ctx.beginPath();
            this.ctx.arc(x, y, size, 0, Math.PI * 2);
            this.ctx.fill();
        }
    }

    drawObjects(objects, cameraX, cameraY, centerX, centerY, scale = 1) {
        if (!objects) return;
    
        for (const obj of objects) {
            if (!obj.is_alive) continue;
    
            // Преобразование мировых координат в экранные
            const screenX = (obj.position.x - cameraX) * scale + centerX;
            const screenY = (obj.position.y - cameraY) * scale + centerY;
    
            // Для титанов специальная отрисовка
            if (obj.type === 'titan' || obj.radius >= 50) {
                this.drawTitan(obj, screenX, screenY, scale);
            } else {
                // Для остальных объектов
                this.ctx.fillStyle = obj.color || '#ffffff';
                this.ctx.beginPath();
                this.ctx.arc(screenX, screenY, obj.radius * scale, 0, Math.PI * 2);
                this.ctx.fill();
            }
    
            // Отрисовка здоровья для объектов с здоровьем
            if (obj.health && obj.health < obj.max_health) {
                this.drawHealthBar(obj, screenX, screenY, scale);
            }
        }
    }
    
    drawTitan(titan, screenX, screenY, scale) {
        // Основной круг титана
        this.ctx.fillStyle = titan.color || '#ffffff';
        this.ctx.beginPath();
        this.ctx.arc(screenX, screenY, titan.radius * scale, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Вторичный цвет для ободка
        this.ctx.strokeStyle = titan.team === 'red' ? '#ff3333' : '#3333ff';
        this.ctx.lineWidth = 3 * scale;
        this.ctx.beginPath();
        this.ctx.arc(screenX, screenY, (titan.radius - 3) * scale, 0, Math.PI * 2);
        this.ctx.stroke();
        
        // Буква "T" в центре
        this.ctx.fillStyle = '#ffffff';
        this.ctx.font = `bold ${titan.radius * 0.6 * scale}px Arial`;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText('T', screenX, screenY);
    }
    
    drawDrones(drones, cameraX, cameraY, centerX, centerY, scale = 1) {
        if (!drones) return;
    
        for (const drone of drones) {
            if (!drone.is_alive) continue;
    
            const screenX = (drone.position.x - cameraX) * scale + centerX;
            const screenY = (drone.position.y - cameraY) * scale + centerY;
            
            // Сохраняем контекст для поворота
            this.ctx.save();
            this.ctx.translate(screenX, screenY);
            
            // Поворачиваем в направлении движения
            const angle = drone.current_angle || drone.direction || 0;
            this.ctx.rotate(angle);
            
            // Корпус дрона (треугольник)
            const radius = drone.radius * scale;
            this.ctx.fillStyle = drone.color || '#ffffff';
            this.ctx.beginPath();
            this.ctx.moveTo(radius, 0);
            this.ctx.lineTo(-radius * 0.7, -radius * 0.8);
            this.ctx.lineTo(-radius * 0.7, radius * 0.8);
            this.ctx.closePath();
            this.ctx.fill();
            
            // Двигатель дрона
            this.ctx.fillStyle = drone.team === 'red' ? '#ff3333' : '#3333ff';
            this.ctx.beginPath();
            this.ctx.arc(-radius * 0.8, 0, radius * 0.4, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Восстанавливаем контекст
            this.ctx.restore();
            
            // Отрисовка здоровья
            if (drone.health && drone.health < drone.max_health) {
                this.drawHealthBar(drone, screenX, screenY, scale);
            }
        }
    }
    
    drawPlayer(player, cameraX, cameraY, centerX, centerY, isCurrentPlayer) {
        if (!player.is_alive) return;
    
        const screenX = (player.position.x - cameraX) + centerX;
        const screenY = (player.position.y - cameraY) + centerY;
    
        // Сохраняем контекст для поворота
        this.ctx.save();
        this.ctx.translate(screenX, screenY);
        
        // Поворачиваем в направлении движения
        this.ctx.rotate(player.direction || 0);
    
        // Корпус корабля (треугольник)
        const radius = player.radius;
        this.ctx.fillStyle = isCurrentPlayer ? '#00ffff' : (player.color || '#5555ff');
        this.ctx.beginPath();
        this.ctx.moveTo(radius, 0);
        this.ctx.lineTo(-radius * 0.7, -radius * 0.8);
        this.ctx.lineTo(-radius * 0.7, radius * 0.8);
        this.ctx.closePath();
        this.ctx.fill();
    
        // Двигатель
        this.ctx.fillStyle = '#ffff00';
        this.ctx.beginPath();
        this.ctx.arc(-radius * 0.8, 0, radius * 0.4, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Оружие
        this.ctx.fillStyle = '#ff5555';
        this.ctx.beginPath();
        this.ctx.arc(radius * 0.7, 0, radius * 0.3, 0, Math.PI * 2);
        this.ctx.fill();
    
        this.ctx.restore();
    
        // Отрисовка прицела для текущего игрока
        if (isCurrentPlayer && !player.is_respawning) {
            this.ctx.save();
            this.ctx.translate(screenX, screenY);
            this.ctx.rotate(player.shooting_direction || player.direction || 0);
    
            this.ctx.strokeStyle = '#00ffff';
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            this.ctx.moveTo(radius * 0.5, 0);
            this.ctx.lineTo(radius * 2, 0);
            this.ctx.stroke();
    
            this.ctx.restore();
        }
    
        // Отрисовка возрождения
        if (player.is_respawning) {
            const alpha = 0.5 + 0.5 * Math.sin(Date.now() / 200);
            this.ctx.globalAlpha = alpha;
    
            this.ctx.strokeStyle = player.color || '#5555ff';
            this.ctx.lineWidth = 3;
            this.ctx.beginPath();
            this.ctx.arc(screenX, screenY, radius + 5, 0, Math.PI * 2);
            this.ctx.stroke();
    
            this.ctx.fillStyle = '#ffffff';
            this.ctx.font = 'bold 16px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            const timeLeft = Math.ceil(player.respawn_timer / 1000);
            this.ctx.fillText(`${timeLeft}`, screenX, screenY);
    
            this.ctx.globalAlpha = 1;
        }
        
        // Отрисовка здоровья
        if (player.health < player.max_health) {
            this.drawHealthBar(player, screenX, screenY, 1);
        }
    }
    
    drawHealthBar(obj, screenX, screenY, scale) {
        const healthPercent = obj.health / obj.max_health;
        const barWidth = obj.radius * 2 * scale;
        const barHeight = 4 * scale;
        const barX = screenX - obj.radius * scale;
        const barY = screenY - obj.radius * scale - 10 * scale;
    
        this.ctx.fillStyle = '#333333';
        this.ctx.fillRect(barX, barY, barWidth, barHeight);
    
        let healthColor;
        if (healthPercent > 0.6) healthColor = '#00ff00';
        else if (healthPercent > 0.3) healthColor = '#ffff00';
        else healthColor = '#ff0000';
    
        this.ctx.fillStyle = healthColor;
        this.ctx.fillRect(barX, barY, barWidth * healthPercent, barHeight);
    }
}

// Запуск клиента при загрузке страницы
window.addEventListener('load', () => {
    window.gameClient = new GameClient();
});