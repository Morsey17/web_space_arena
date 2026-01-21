from objects.game_object import *

class Drone(GameObject):
    def __init__(self, id: str, position: Vector2D, team: str, titan_id: str):
        super().__init__(id, position, team)
        self.radius = 8
        self.direction = Vector2D(1, 0)
        self.speed = 2
        self.rotation_speed = 3
        self.health = 30
        self.titan_id = titan_id
        self.target = None

    def update(self, enemies: List[GameObject]):
        # Находим ближайшего врага
        if not self.target or not self.target.alive:
            closest = None
            closest_dist = float('inf')

            for enemy in enemies:
                if enemy.team != self.team and enemy.alive:
                    dist = (self.position - enemy.position).length()
                    if dist < closest_dist:
                        closest_dist = dist
                        closest = enemy

            self.target = closest

        # Двигаемся к цели
        if self.target and self.target.alive:
            direction_to_target = (self.target.position - self.position).normalized()

            # Плавно поворачиваем к цели
            current_angle = math.degrees(math.atan2(self.direction.y, self.direction.x))
            target_angle = math.degrees(math.atan2(direction_to_target.y, direction_to_target.x))

            angle_diff = (target_angle - current_angle + 180) % 360 - 180

            if abs(angle_diff) > self.rotation_speed:
                angle_diff = math.copysign(self.rotation_speed, angle_diff)

            new_angle = current_angle + angle_diff
            self.direction = Vector2D(1, 0).rotate(new_angle)

        # Двигаемся
        self.position = self.position + self.direction * self.speed

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'type': 'drone',
            'direction_x': self.direction.x,
            'direction_y': self.direction.y
        })
        return data