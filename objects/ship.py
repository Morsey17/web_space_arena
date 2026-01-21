from objects.game_object import *

class Ship(GameObject):
    def __init__(self, id: str, position: Vector2D, team: str, player_id: str = None):
        super().__init__(id, position, team)
        self.radius = 15
        self.direction = Vector2D(1, 0)  # Направление движения
        self.speed = 3
        self.rotation_speed = 5  # градусов за тик
        self.target_rotation = 0
        self.health = 100
        self.max_health = 100
        self.shoot_cooldown = 0
        self.player_id = player_id  # ID игрока, который управляет
        self.is_bot = player_id is None

    def update(self):
        # Поворачиваем к цели
        current_angle = math.degrees(math.atan2(self.direction.y, self.direction.x))
        angle_diff = (self.target_rotation - current_angle + 180) % 360 - 180

        if abs(angle_diff) > self.rotation_speed:
            angle_diff = math.copysign(self.rotation_speed, angle_diff)

        new_angle = current_angle + angle_diff
        self.direction = Vector2D(1, 0).rotate(new_angle)

        # Двигаемся
        self.position = self.position + self.direction * self.speed

        # Ограничиваем поле
        self.position.x = max(50, min(950, self.position.x))
        self.position.y = max(50, min(550, self.position.y))

        # Перезарядка
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'type': 'ship',
            'direction_x': self.direction.x,
            'direction_y': self.direction.y,
            'health': self.health,
            'max_health': self.max_health,
            'player_id': self.player_id
        })
        return data