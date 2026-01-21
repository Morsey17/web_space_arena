from objects.game_object import *

class Missile(GameObject):
    def __init__(self, id: str, position: Vector2D, team: str, target: GameObject, damage: int = 25):
        super().__init__(id, position, team)
        self.radius = 6
        self.target = target
        self.speed = 4
        self.turn_rate = 3  # градусов за тик
        self.direction = Vector2D(1, 0)
        self.damage = damage

    def update(self):
        if not self.target or not self.target.alive:
            self.alive = False
            return

        # Поворачиваем к цели
        direction_to_target = (self.target.position - self.position).normalized()

        current_angle = math.degrees(math.atan2(self.direction.y, self.direction.x))
        target_angle = math.degrees(math.atan2(direction_to_target.y, direction_to_target.x))

        angle_diff = (target_angle - current_angle + 180) % 360 - 180

        if abs(angle_diff) > self.turn_rate:
            angle_diff = math.copysign(self.turn_rate, angle_diff)

        new_angle = current_angle + angle_diff
        self.direction = Vector2D(1, 0).rotate(new_angle)

        # Двигаемся
        self.position = self.position + self.direction * self.speed

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'type': 'missile',
            'direction_x': self.direction.x,
            'direction_y': self.direction.y,
            'target_id': self.target.id if self.target else None
        })
        return data