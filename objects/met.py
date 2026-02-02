from objects.game_object import *

class Met(GameObject):
    def __init__(self, position: Vector2D, radius: float):
        super().__init__(position, radius)
        self.max_value = 100
        self.value = 40
        self.time = 0
        self.max_time = 50

    def update(self):
        self.time -= 1
        if self.time <= 0:
            if self.value < self.max_value:
                self.value += 1
            self.time = self.max_time

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'type': 'met',
            'value': self.value,
            'max_value': self.max_value
        })
        return data