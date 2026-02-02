from objects.game_object import *

class Missile(GameObject):
    def __init__(self, parent, target):
        super().__init__(parent.position, 8)
        self.team = parent.team
        self.speed = 13
        self.rotate_speed = 5
        self.damage = 7
        self.lifetime = 40
        self.alive = True
        self.target = target
        self.direction = (self.target.position - self.position).norm().normalized()
    """
    def __init__(self, id: str, position: Vector2D, team: str, target: GameObject, damage: int = 25):
        super().__init__(id, position, team)
        self.radius = 6
        self.target = target
        self.speed = 4
        self.turn_rate = 3  # градусов за тик
        self.direction = Vector2D(1, 0)
        self.damage = damage
    """

    def update(self, enemies):
        if not self.target or not self.target.alive:
            self.alive = False
            return


        self.lifetime -= 1
        touch = False
        for obj in enemies:
            if self.collides_with(obj):
                touch = True
                obj.health -= self.damage
                if obj.health <= 0:
                    obj.alive = False
                break
        if (self.lifetime <= 0) or (touch):
            self.alive = False
            return

        # Поворачиваем к цели
        direction_to_target = (self.target.position - self.position).norm().normalized()

        current_angle = math.degrees(math.atan2(self.direction.y, self.direction.x))
        target_angle = math.degrees(math.atan2(direction_to_target.y, direction_to_target.x))

        angle_diff = (target_angle - current_angle + 180) % 360 - 180

        if abs(angle_diff) > self.rotate_speed:
            angle_diff = math.copysign(self.rotate_speed, angle_diff)

        new_angle = current_angle + angle_diff
        self.direction = Vector2D(1, 0).rotate(new_angle)

        # Двигаемся
        self.position = self.position + self.direction * self.speed

    def destroy(self, list):
        try:
            if list is not None and self in list:
                list.remove(self)
        except Exception as e:
            print(f"Ошибка при удалении объекта: {e}")

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'type': 'missile',
            'speed': self.speed,
            'direction_x': self.direction.x,
            'direction_y': self.direction.y
        })
        return data