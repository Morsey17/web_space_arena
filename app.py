# scp flask-game.tar root@92.118.114.86:/tmp/
# 1w5LLhwVCQAb7S23-

# s2

"""

sudo docker run -d \
  --name flask-game \
  -p 8080:5000 \
  --restart always \
  flask-game

openssl x509 -in /root/tss-server/ssl/cert.pem -noout -dates
        подключение к серверу:
ssh root@92.118.114.86
cd \tmp

"""

def debug_error(func):
    """Декоратор для отладки ошибок"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            import traceback
            tb = traceback.extract_tb(e.__traceback__)[-1]  # Берем последний кадр
            print(f"Ошибка в функции {tb.name}")
            print(f"Файл: {tb.filename}, Строка: {tb.lineno}")
            print(f"Код: {tb.line}")
            raise
    return wrapper

@debug_error
def example():
    return 1 / 0



from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, emit
import math
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple
import time

app = Flask(__name__)
app.config['STATIC_FOLDER'] = 'static'

# Для отдачи статических файлов (если нужно)
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


class Player:
    def __init__(self, sid, team):
        self.sid = sid
        self.ship = None
        self.team = team
        self.cooldown = 100
        self.max_cooldown = 100

    def destroy(self, list):
        try:
            self.ship.alive = False
            if list is not None and self in list:
                list.remove(self)
        except Exception as e:
            print(f"Ошибка при удалении объекта: {e}")


players = []


# Используем threading mode для совместимости с Python 3.13
socketio = SocketIO(app,
                    cors_allowed_origins="*",
                    async_mode='threading',
                    logger=False,
                    engineio_logger=False)


# ========== КЛАССЫ ИГРЫ ==========


#from objects.game_object import *
from objects.titan import *
from objects.ship import *
from objects.drone import *
from objects.tower import *
from objects.bullet import *
from objects.missile import *
from objects.explosion import *
from objects.gold import *
from objects.met import *



# ========== КЛАСС ИГРЫ ==========

class Game:
    def __init__(self):
        self.ship = [[], []]
        self.bullet = [[], []]
        self.missile = [[], []]
        self.missile = [[], []]
        self.drone = [[], []]
        self.titan = [[], []]
        self.tower = [[], []]
        self.explosion = []
        self.gold = []
        self.met = []
        self.width = 4000
        self.height = 4000
        self.objects = {}
        self.last_id = 0
        self.running = True
        self.restart = False

        # Создаем титанов
        self.create_titans()

        # Создаём метеориты
        self.create_mets()

        # Создаем башни
        self.create_towers()

    def create_mets(self):
        x = 3000
        y = 1000
        self.met.append(Met(Vector2D(x - 900, y - 300), 100))
        self.met.append(Met(Vector2D(x + 400, y - 700), 120))
        self.met.append(Met(Vector2D(x + 40, y + 300), 110))
        x = 1000
        y = 3000
        self.met.append(Met(Vector2D(x - 900, y - 300), 100))
        self.met.append(Met(Vector2D(x + 400, y - 700), 120))
        self.met.append(Met(Vector2D(x + 40, y + 300), 110))

    def create_titans(self):
        self.titan[0].append(Titan(Vector2D(1000, 1000), 0))
        self.titan[1].append(Titan(Vector2D(3000, 3000), 1))

    def create_towers(self):
        for team_i in range(2):
            for i in range(3):
                orbit_angle = i * 120  # Равномерно распределяем
                self.tower[team_i].append(Tower(
                    Vector2D(0, 0),
                    self.titan[team_i][0],
                    orbit_angle
                ))

    def spawn_bullet(self, parent):
        self.bullet[parent.team].append(Bullet(parent))

    def spawn_missile(self, parent, target=None):
        if target != None:
            self.missile[parent.team].append(Missile(parent, target))

    def add_ship(self, team: int, sid: int):
        self.ship[team].append(Ship(
            team,
            sid,
            self.titan[team][0],
            "simple"
        ))

    def spawn_drone(self, titan: Titan):
        if len(self.drone[titan.team]) < 20:
            self.drone[titan.team].append(Drone(titan))

    """

    def add_ship(self, player_id: str, team_i: int):
        # Создаем корабль
        spawn_pos = Game.titan.position + Vector2D(0, -150)
        ship = Ship(
            self.generate_id(),
            spawn_pos,
            team,
            player_id
        )

        self.objects[ship.id] = ship
        self.players[player_id] = ship.id

    def spawn_drone(self, titan: Titan):
        offset = Vector2D(random.uniform(-50, 50), random.uniform(-50, 50))
        drone = Drone(
            self.generate_id(),
            titan.position + offset,
            titan.team,
            titan.id
        )
        self.objects[drone.id] = drone
    """

    def update(self):

        if not self.running:
            return

        for player in players:
            player.cooldown -= 1
            if (player.ship == None):
                if (player.cooldown <= 0):
                    game.add_ship(player.team, player.sid)
                    player.ship = game.ship[player.team][-1]
            elif (player.ship.health <= 0):
                player.cooldown = player.max_cooldown
                player.ship = None

        for team_i in range(2):
            enemy_i = 1 if team_i == 0 else 0
            enemies = (self.titan[enemy_i] + self.tower[enemy_i] +
                       self.ship[enemy_i] + self.drone[enemy_i])
            for obj in self.titan[team_i]:
                if obj.update():
                    self.spawn_drone(obj)
            for obj in self.tower[team_i]:
                self.spawn_missile(obj, obj.update(enemies))
            for obj in self.drone[team_i]:
                if obj.update(enemies):
                    self.spawn_bullet(obj)
            for obj in self.ship[team_i]:
                if obj.update(self):
                    self.spawn_bullet(obj)
            for obj in self.bullet[team_i]:
                obj.update(enemies, game)
            for obj in self.missile[team_i]:
                obj.update(enemies)
            # Удаление из памяти мёртвых
            for obj in self.bullet[team_i]:
                if obj.alive == False:
                    #position: Vector2D, radius: float, team: int, lifetime=10):
                    self.explosion.append(Explosion(obj.position, obj.radius, obj.team, 10))
                    obj.destroy(self.bullet[team_i])
            for obj in self.missile[team_i]:
                if obj.alive == False:
                    self.explosion.append(Explosion(obj.position, obj.radius, obj.team, 10))
                    obj.destroy(self.missile[team_i])
            for obj in self.drone[team_i]:
                if obj.alive == False:
                    self.explosion.append(Explosion(obj.position, obj.radius * 1.5, obj.team, 30))
                    self.gold.append(Gold(obj.position, 5))
                    obj.destroy(self.drone[team_i])
            for obj in self.ship[team_i]:
                if obj.alive == False:
                    self.explosion.append(Explosion(obj.position, obj.radius, obj.team, 50))
                    self.gold.append(Gold(obj.position, 10 + obj.gold / 5))
                    obj.destroy(self.ship[team_i])
            for obj in self.tower[team_i]:
                if obj.alive == False:
                    self.explosion.append(Explosion(obj.position, obj.radius, obj.team, 70))
                    self.gold.append(Gold(obj.position, 100))
                    obj.destroy(self.tower[team_i])

        for obj in self.met:
            obj.update()
        for obj in self.explosion:
            obj.update()
            if obj.alive == False:
                obj.destroy(self.explosion)
        for obj in self.gold:
            obj.update(game)
            if obj.alive == False:
                obj.destroy(self.gold)


        # Обновление координат для закцикливания карты
        for team_i in range(2):
            objs = self.titan[team_i] + self.tower[team_i] + self.ship[team_i] + self.drone[team_i] \
                + self.bullet[team_i] + self.missile[team_i]
            for obj in objs:
                obj.norm_position()


    def get_game_state(self):
        return {
            'team': [
                {'name': 'red', 'color': '#ff0000'},
                {'name': 'blue', 'color': '#0000ff'}
            ],
            'titan': [[obj.to_dict() for obj in game.titan[0]], [obj.to_dict() for obj in game.titan[1]]],
            'tower': [[obj.to_dict() for obj in game.tower[0]], [obj.to_dict() for obj in game.tower[1]]],
            'drone': [[obj.to_dict() for obj in game.drone[0]], [obj.to_dict() for obj in game.drone[1]]],
            'ship': [[obj.to_dict() for obj in game.ship[0]], [obj.to_dict() for obj in game.ship[1]]],
            'bullet': [[obj.to_dict() for obj in game.bullet[0]], [obj.to_dict() for obj in game.bullet[1]]],
            'missile': [[obj.to_dict() for obj in game.missile[0]], [obj.to_dict() for obj in game.missile[1]]],
            'explosion': [obj.to_dict() for obj in game.explosion],
            'gold': [obj.to_dict() for obj in game.gold],
            'met': [obj.to_dict() for obj in game.met]
        }

# ========== СЕРВЕР ==========

game = Game()


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    emit('connect', {'sid': request.sid})


@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    for player in players:
        if player.sid == sid:
            player.destroy(players)
    """
    if player_id in game.players:
        ship_id = game.players[player_id]
        if ship_id in game.objects:
            game.objects[ship_id].alive = False
        del game.players[player_id]
    """

    print(f'Client disconnected: {sid}')


@socketio.on('join_team')
def handle_join_team(data):
    team_i = data.get('team')
    sid = request.sid

    players.append(Player(sid, team_i))
    game.add_ship(team_i, sid)

    emit('joined', {'result': 'success'})


@socketio.on('player_keydown')
def handle_player_input(data):
    key = data.get('key')
    sid = request.sid
    #game.handle_player_input(sid, key)
    for team in range(2):
        for ship in game.ship[team]:
            if sid == ship.sid:
                ship.button[key] = True
                return

@socketio.on('player_keyup')
def handle_player_input(data):
    key = data.get('key')
    sid = request.sid
    #game.handle_player_input(sid, key)
    for team in range(2):
        for ship in game.ship[team]:
            if sid == ship.sid:
                ship.button[key] = False
                return


# Игровой цикл
def game_loop():
    while True:

        try:
            global game
            game.update()
            socketio.emit('game_state', game.get_game_state())
            time.sleep(1 / 60)  # 60 FPS
            if game.restart:
                del game
                game = Game()
        except Exception as e:
            print(f"Error in game loop: {e}")
            time.sleep(1)


if __name__ == '__main__':
    # Запускаем игровой цикл в отдельном потоке
    import threading

    thread = threading.Thread(target=game_loop, daemon=True)
    thread.start()

    print("Server starting on https://0.0.0.0:5000")

    # Пути к SSL сертификатам
    ssl_cert = '/app/ssl/cert.pem'
    ssl_key = '/app/ssl/key.pem'

    # Проверяем наличие сертификатов
    import os

    if os.path.exists(ssl_cert) and os.path.exists(ssl_key):
        ssl_context = (ssl_cert, ssl_key)
    else:
        ssl_context = None
        print("SSL сертификаты не найдены, запуск без HTTPS")

    # Запускаем с SSL
    socketio.run(app,
                 host='0.0.0.0',
                 port=5000,
                 debug=True,
                 allow_unsafe_werkzeug=True,
                 ssl_context=ssl_context)