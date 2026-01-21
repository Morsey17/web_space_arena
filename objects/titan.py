from objects.game_object import *

class Titan(GameObject):
    def __init__(self, id: str, position: Vector2D, team: str):
        super().__init__(id, position, team)
        self.radius = 80
        self.health = 1000
        self.max_health = 1000
        self.drone_spawn_timer = 0

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'type': 'titan',
            'health': self.health,
            'max_health': self.max_health
        })
        return data