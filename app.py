from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import math
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple
import time

app = Flask(__name__)

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



# ========== КЛАСС ИГРЫ ==========

class Game:
    def __init__(self):
        self.width = 1000
        self.height = 600
        self.objects = {}
        self.last_id = 0
        self.players = {}
        self.running = True

        # Создаем титанов
        self.create_titans()

        # Создаем башни
        self.create_towers()

    def generate_id(self) -> str:
        self.last_id += 1
        return f"obj_{self.last_id}"

    def create_titans(self):
        red_titan = Titan(self.generate_id(), Vector2D(200, 300), "red")
        blue_titan = Titan(self.generate_id(), Vector2D(800, 300), "blue")

        self.objects[red_titan.id] = red_titan
        self.objects[blue_titan.id] = blue_titan

    def create_towers(self):
        # Находим титанов
        titans = [obj for obj in self.objects.values() if isinstance(obj, Titan)]

        for titan in titans:
            for i in range(3):  # 3 башни на каждого титана
                tower = Tower(
                    self.generate_id(),
                    Vector2D(0, 0),
                    titan.team,
                    titan.id
                )
                tower.orbit_angle = i * 120  # Равномерно распределяем
                self.objects[tower.id] = tower

    def add_ship(self, player_id: str, team: str) -> str:
        # Находим титана команды
        titan = next((obj for obj in self.objects.values()
                      if isinstance(obj, Titan) and obj.team == team), None)

        if not titan:
            return None

        # Создаем корабль
        spawn_pos = titan.position + Vector2D(0, -150)
        ship = Ship(
            self.generate_id(),
            spawn_pos,
            team,
            player_id
        )

        self.objects[ship.id] = ship
        self.players[player_id] = ship.id

        return ship.id

    def spawn_drone(self, titan: Titan):
        offset = Vector2D(random.uniform(-50, 50), random.uniform(-50, 50))
        drone = Drone(
            self.generate_id(),
            titan.position + offset,
            titan.team,
            titan.id
        )
        self.objects[drone.id] = drone

    def update(self):
        if not self.running:
            return

        # Обновляем все объекты
        ships = []
        enemies = []
        bullets = []
        missiles = []
        drones = []
        titans = []
        towers = []

        # Собираем объекты по типам
        for obj in list(self.objects.values()):
            if isinstance(obj, Ship):
                ships.append(obj)
                obj.update()
            elif isinstance(obj, Drone):
                drones.append(obj)
                enemies.append(obj)  # Дроны всегда враги для противоположной команды
            elif isinstance(obj, Bullet):
                bullets.append(obj)
                obj.update()
            elif isinstance(obj, Missile):
                missiles.append(obj)
                obj.update()
            elif isinstance(obj, Tower):
                towers.append(obj)
            elif isinstance(obj, Titan):
                titans.append(obj)

        # Обновляем дронов и башни
        for drone in drones:
            # Собираем врагов для дрона
            drone_enemies = []
            for obj in self.objects.values():
                if obj.team != drone.team and obj.alive:
                    drone_enemies.append(obj)
            drone.update(drone_enemies)

        for tower in towers:
            # Находим титана башни
            titan = self.objects.get(tower.titan_id)
            if not titan:
                continue

            # Собираем враги
            tower_enemies = []
            for obj in self.objects.values():
                if obj.team != tower.team and obj.alive:
                    tower_enemies.append(obj)

            target = tower.update(titan, tower_enemies)
            if target:
                # Создаем ракету
                missile = Missile(
                    self.generate_id(),
                    tower.position,
                    tower.team,
                    target
                )
                self.objects[missile.id] = missile

        # Спавним дронов у титанов
        for titan in titans:
            titan.drone_spawn_timer += 1
            if titan.drone_spawn_timer >= 180:  # 3 секунды
                titan.drone_spawn_timer = 0
                self.spawn_drone(titan)

        # Проверка столкновений
        self.check_collisions()

        # Удаляем мертвые объекты
        dead_ids = [obj_id for obj_id, obj in self.objects.items() if not obj.alive]
        for obj_id in dead_ids:
            del self.objects[obj_id]

            # Если это корабль игрока
            for player_id, ship_id in list(self.players.items()):
                if ship_id == obj_id:
                    del self.players[player_id]

    def check_collisions(self):
        objects_list = list(self.objects.values())

        for i in range(len(objects_list)):
            obj1 = objects_list[i]
            if not obj1.alive:
                continue

            for j in range(i + 1, len(objects_list)):
                obj2 = objects_list[j]
                if not obj2.alive:
                    continue

                if obj1.collides_with(obj2):
                    self.handle_collision(obj1, obj2)

    def handle_collision(self, obj1, obj2):
        # Пули и ракеты с любыми объектами
        if isinstance(obj1, Bullet):
            if obj2.team != obj1.team:
                obj2.health -= obj1.damage
                if obj2.health <= 0:
                    obj2.alive = False
                obj1.alive = False
        elif isinstance(obj2, Bullet):
            if obj1.team != obj2.team:
                obj1.health -= obj2.damage
                if obj1.health <= 0:
                    obj1.alive = False
                obj2.alive = False

        # Ракеты
        elif isinstance(obj1, Missile):
            if obj2.team != obj1.team:
                obj2.health -= obj1.damage
                if obj2.health <= 0:
                    obj2.alive = False
                obj1.alive = False
        elif isinstance(obj2, Missile):
            if obj1.team != obj2.team:
                obj1.health -= obj2.damage
                if obj1.health <= 0:
                    obj1.alive = False
                obj2.alive = False

        # Столкновения кораблей с дронами
        elif isinstance(obj1, Ship) and isinstance(obj2, Drone):
            if obj1.team != obj2.team:
                obj1.health -= 20
                obj2.health -= 50
                if obj1.health <= 0:
                    obj1.alive = False
                if obj2.health <= 0:
                    obj2.alive = False
        elif isinstance(obj2, Ship) and isinstance(obj1, Drone):
            if obj2.team != obj1.team:
                obj2.health -= 20
                obj1.health -= 50
                if obj2.health <= 0:
                    obj2.alive = False
                if obj1.health <= 0:
                    obj1.alive = False

    def get_game_state(self):
        return {
            'width': self.width,
            'height': self.height,
            'objects': {obj_id: obj.to_dict() for obj_id, obj in self.objects.items()}
        }

    def handle_player_input(self, player_id: str, key: str):
        ship_id = self.players.get(player_id)
        if not ship_id:
            return

        ship = self.objects.get(ship_id)
        if not ship or not ship.alive:
            return

        if key == 'A':
            ship.target_rotation += ship.rotation_speed
        elif key == 'D':
            ship.target_rotation -= ship.rotation_speed
        elif key == 'SPACE':
            if ship.shoot_cooldown <= 0:
                ship.shoot_cooldown = 10  # 0.17 секунды при 60 FPS

                # Создаем пулю
                bullet = Bullet(
                    self.generate_id(),
                    ship.position + ship.direction * (ship.radius + 5),
                    ship.direction,
                    ship.team
                )
                self.objects[bullet.id] = bullet


# ========== СЕРВЕР ==========

game = Game()


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')


@socketio.on('disconnect')
def handle_disconnect():
    player_id = request.sid
    if player_id in game.players:
        ship_id = game.players[player_id]
        if ship_id in game.objects:
            game.objects[ship_id].alive = False
        del game.players[player_id]

    print(f'Client disconnected: {player_id}')


@socketio.on('join_team')
def handle_join_team(data):
    team = data.get('team', 'red')
    player_id = request.sid

    # Удаляем старый корабль, если был
    if player_id in game.players:
        old_ship_id = game.players[player_id]
        if old_ship_id in game.objects:
            game.objects[old_ship_id].alive = False

    # Добавляем новый корабль
    ship_id = game.add_ship(player_id, team)

    emit('joined', {'team': team, 'ship_id': ship_id})


@socketio.on('player_input')
def handle_player_input(data):
    key = data.get('key')
    player_id = request.sid
    game.handle_player_input(player_id, key)


# Игровой цикл
def game_loop():
    while True:
        try:
            game.update()
            socketio.emit('game_state', game.get_game_state())
            time.sleep(1 / 60)  # 60 FPS
        except Exception as e:
            print(f"Error in game loop: {e}")
            time.sleep(1)


if __name__ == '__main__':
    # Запускаем игровой цикл в отдельном потоке
    import threading

    thread = threading.Thread(target=game_loop, daemon=True)
    thread.start()

    print("Server starting on http://localhost:5000")
    # Добавляем allow_unsafe_werkzeug=True для работы с Werkzeug
    socketio.run(app, debug=True, port=5000, use_reloader=False, allow_unsafe_werkzeug=True)