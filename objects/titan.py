from objects.game_object import *

class Titan(GameObject):
    def __init__(self, position: Vector2D, team: int):
        super().__init__(position, 120)
        self.team = team
        self.max_health = 4000
        self.health = self.max_health
        self.max_drone_spawn_timer = 100
        self.drone_spawn_timer = self.max_drone_spawn_timer
        self.alive = True

    def update(self):
        if self.drone_spawn_timer > 0:
            self.drone_spawn_timer -= 1
            if self.drone_spawn_timer == 0:
                self.drone_spawn_timer = self.max_drone_spawn_timer
                return True
        return False


    def to_dict(self):
        data = super().to_dict()
        data.update({
            'type': 'titan',
            'health': self.health / self.max_health,
            'spawn_drone_progress': self.drone_spawn_timer / self.max_drone_spawn_timer
        })
        return data