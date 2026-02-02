from objects.game_object import *
from objects.titan import *

class Tower(GameObject):
    def __init__(self, position: Vector2D, titan: Titan, orbit_angle):
        super().__init__(position, 40)
        self.team = titan.team
        self.radius = 40
        self.titan = titan
        self.max_health = 800
        self.health = self.max_health
        self.orbit_radius = 160
        self.orbit_speed = 0.25
        self.shoot_cooldown = 0
        self.max_shoot_cooldown = 6
        self.orbit_angle = orbit_angle
        self.attack_range = 200
        self.alive = True

    def update(self, enemies):
        # Движение по орбите
        self.orbit_angle += self.orbit_speed
        self.orbit_angle %= 360

        offset = Vector2D(
            math.cos(math.radians(self.orbit_angle)) * self.orbit_radius,
            math.sin(math.radians(self.orbit_angle)) * self.orbit_radius
        )
        self.position = self.titan.position + offset

        # Стрельба
        self.shoot_cooldown -= 1
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.max_shoot_cooldown
            closest = None
            closest_dist = self.attack_range
            for enemy in enemies:
                distance = self.get_distance_to_obj(enemy)
                if distance < closest_dist:
                    closest_dist = distance
                    closest = enemy
            if closest != None:
                return closest
        return None

    def destroy(self, list):
        try:
            if list is not None and self in list:
                list.remove(self)
        except Exception as e:
            print(f"Ошибка при удалении объекта: {e}")

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'type': 'tower',
            'health': self.health / self.max_health,
        })
        return data