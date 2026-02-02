from objects.game_object import *

class Explosion(GameObject):
    def __init__(self, position: Vector2D, radius: float, team: int, lifetime=10):
        super().__init__(position, radius)
        self.team = team
        self.alive = True
        self.lifetime = lifetime
        self.max_lifetime = lifetime

    def update(self):
        self.radius *= 1.05
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False

    def destroy(self, list):
        try:
            if list is not None and self in list:
                list.remove(self)
        except Exception as e:
            print(f"Ошибка при удалении объекта: {e}")

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'type': 'explosion',
            'team': self.team,
            'lifetime': self.lifetime / self.max_lifetime
        })
        return data