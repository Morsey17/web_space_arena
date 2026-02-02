from objects.game_object import *

class Gold(GameObject):
    def __init__(self, position: Vector2D, value: int):
        super().__init__(position, math.sqrt(value))
        self.value = value
        self.speed = 10
        self.range = 200
        self.lifetime = 5000
        self.alive = True

    def update(self, game):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False
            return

        min_distance = 1000
        target = None
        for i in range(2):
            for ship in game.ship[i]:
                distance = self.get_distance_to_obj(ship) #(self.position - enemy.position).length()
                if distance < min_distance:
                    min_distance = distance
                    target = ship
        if (target != None) and (min_distance < self.range):
            if min_distance < 20:
                target.update_gold(self.value)
                self.alive = False
            else:
                direction = (self.position - target.position).norm().normalized()
                self.position = self.position - direction * 7

    def destroy(self, list):
        try:
            if list is not None and self in list:
                list.remove(self)
        except Exception as e:
            print(f"Ошибка при удалении объекта: {e}")

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'type': 'gold',
            'value': self.value
        })
        return data