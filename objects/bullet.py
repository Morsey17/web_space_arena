from objects.game_object import *

class Bullet(GameObject):
    def __init__(self, id: str, position: Vector2D, direction: Vector2D, team: str, damage: int = 10):
        super().__init__(id, position, team)
        self.radius = 4
        self.direction = direction
        self.speed = 8
        self.damage = damage
        self.lifetime = 180  # 3 секунды при 60 FPS

    def update(self):
        self.position = self.position + self.direction * self.speed
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'type': 'bullet',
            'direction_x': self.direction.x,
            'direction_y': self.direction.y
        })
        return data