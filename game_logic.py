from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import random
import time
import threading
import math

from objects.ship import Ship

"""from objects.titan import Titan
from objects.tower import Tower
from objects.drone import Drone
from objects.bullet import Bullet
from objects.missile import Missile
from objects.player import Player
from objects.explosion import Explosion"""

# Параметры игры
MAP_SIZE = 10000
STAR_COUNT = 500


class Team:
    def __init__(self):
        self.name = "Avava"
        self.titan = []
        self.tower = []
        self.drone = []
        self.ship = []


team = Team()


def create_ship(sid):
    return team.ship.append(Ship(sid, 0, 0, 0, 10))


def game_loop():
    for ship in team.ship:
        ship.update()
        #current_time = time.time()
        #dt = min(0.033, current_time - game_state['last_update'])  # ~30 FPS max



"""
class Player:
    def __init__(self, sid):
        self.sid = sid
        self.x = 0
        self.y = 0
        self.rotation = 0  # в градусах
        self.color = f'hsl({random.randint(0, 360)}, 100%, 50%)'
        self.last_input = {'a': False, 'd': False}

    def to_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'rotation': self.rotation,
            'color': self.color
        }


class Star:
    def __init__(self):
        self.x = random.uniform(-MAP_SIZE / 2, MAP_SIZE / 2)
        self.y = random.uniform(-MAP_SIZE / 2, MAP_SIZE / 2)
        self.size = random.uniform(0.5, 2)

    def to_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'size': self.size
        }


# Инициализация звёзд
for _ in range(STAR_COUNT):
    game_state['stars'].append(Star())


def game_loop():
    while True:
        current_time = time.time()
        dt = min(0.033, current_time - game_state['last_update'])  # ~30 FPS max

        # Обновление игроков
        for player in list(game_state['players'].values()):
            # Поворот
            if player.last_input['a']:
                player.rotation = (player.rotation - TURN_SPEED) % 360
            if player.last_input['d']:
                player.rotation = (player.rotation + TURN_SPEED) % 360

            # Движение вперёд
            rad = math.radians(player.rotation)
            player.x += math.sin(rad) * PLAYER_SPEED
            player.y -= math.cos(rad) * PLAYER_SPEED  # Ось Y инвертирована для canvas

        # Отправка обновлений всем подключённым клиентам
        state = {
            'players': {sid: p.to_dict() for sid, p in game_state['players'].items()},
            'stars': [star.to_dict() for star in game_state['stars']]
        }

        socketio.emit('game_update', state, namespace='/')
        game_state['last_update'] = current_time
        time.sleep(0.033)  # ~30 FPS


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    player = Player(request.sid)
    game_state['players'][request.sid] = player

    # Отправляем начальное состояние
    emit('init', player.to_dict())


@socketio.on('player_input')
def handle_player_input(data):
    sid = request.sid
    if sid in game_state['players']:
        game_state['players'][sid].last_input = data


@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    if sid in game_state['players']:
        del game_state['players'][sid]
    print(f'Client disconnected: {sid}')


if __name__ == '__main__':
    # Запускаем игровой цикл в отдельном потоке
    game_thread = threading.Thread(target=game_loop, daemon=True)
    game_thread.start()

    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
"""