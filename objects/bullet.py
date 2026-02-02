def debug_error(func):
    """Декоратор для отладки ошибок"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            import traceback
            tb = traceback.extract_tb(e.__traceback__)[-1]  # Берем последний кадр
            print(f"Ошибка в функции {tb.name}")
            print(f"Файл: {tb.filename}, Строка: {tb.lineno}")
            print(f"Код: {tb.line}")
            raise
    return wrapper

@debug_error
def example():
    return 1 / 0

from objects.game_object import *

class Bullet(GameObject):
    def __init__(self, parent):
        super().__init__(parent.position, parent.bullet_radius)
        self.team = parent.team
        self.direction = parent.direction
        self.speed = Config.bullet_speed
        self.damage = parent.shoot_damage
        self.lifetime = Config.bullet_alive_time  # 3 секунды при 60 FPS
        self.alive = True

    def update(self, enemies, game):
        self.position = self.position + self.direction * self.speed
        self.lifetime -= 1
        touch = False
        for obj in enemies:
            if self.collides_with(obj):
                touch = True
                obj.health -= self.damage
                if obj.health <= 0:
                    obj.alive = False
                break
        if touch == False:
            for obj in game.met:
                if self.collides_with(obj):
                    if obj.value > 0:
                        touch = True
                        value = min(obj.value, 5)
                        obj.value -= value
                        obj.time = 250
                        from objects.gold import Gold
                        game.gold.append(Gold(self.position, value))
                        break
        if (self.lifetime <= 0) or (touch):
            self.alive = False
            return

    def destroy(self, list):
        try:
            if list is not None and self in list:
                list.remove(self)
        except Exception as e:
            print(f"Ошибка при удалении объекта: {e}")

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'type': 'bullet',
            'speed': self.speed,
            'direction_x': self.direction.x,
            'direction_y': self.direction.y
        })
        return data