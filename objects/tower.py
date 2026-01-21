from objects.game_object import *
from objects.titan import *

class Tower(GameObject):
    def __init__(self, id: str, position: Vector2D, team: str, titan_id: str):
        super().__init__(id, position, team)
        self.radius = 20
        self.titan_id = titan_id
        self.orbit_radius = 120
        self.orbit_speed = 0.5
        self.orbit_angle = random.uniform(0, 360)
        self.shoot_timer = 0
        self.attack_range = 250

    def update(self, titan: Titan, enemies: List[GameObject]):
        # Движение по орбите
        self.orbit_angle += self.orbit_speed
        self.orbit_angle %= 360

        offset = Vector2D(
            math.cos(math.radians(self.orbit_angle)) * self.orbit_radius,
            math.sin(math.radians(self.orbit_angle)) * self.orbit_radius
        )
        self.position = titan.position + offset

        # Стрельба
        self.shoot_timer += 1
        if self.shoot_timer >= 60:  # Секунда при 60 FPS
            # Ищем врага в радиусе
            for enemy in enemies:
                if enemy.team != self.team and enemy.alive:
                    dist = (self.position - enemy.position).length()
                    if dist <= self.attack_range:
                        self.shoot_timer = 0
                        return enemy
        return None

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'type': 'tower'
        })
        return data