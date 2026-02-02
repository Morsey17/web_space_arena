from objects.game_object import *
from objects.titan import Titan


class Ship(GameObject):
    def __init__(self, team: int, sid: int, titan: Titan, tip: str):
        super().__init__(titan.position, Config.ship_radius)
        self.team = team
        self.sid = sid
        self.tip = tip
        self.titan = titan
        self.team = titan.team
        self.gold = 0
        self.alive = False
        self.direction = Vector2D(1, 0)  # Направление движения
        self.speed = Config.ship_speed

        self.bullet_radius = Config.ship_bullet_radius

        self.rotation_speed = 2  # градусов за тик
        self.target_rotation = 0

        self.health = Config.ship_health
        self.max_health = Config.ship_health

        self.shoot_damage = Config.ship_shoot_damage
        self.shoot_cooldown = 0
        self.max_shoot_cooldown = Config.ship_shoot_cooldown

        self.is_bot = False
        self.alive = True
        self.admin = False
        self.admin_num = 0
        self.button = {'A': False, 'D': False, 'O': False, 'P': False, 'SPACE': False}
        self.alive = True

    def update(self, game):
        if self.button['O']:
            self.admin_num += 1
            if self.admin_num > 250:
                self.admin = True
        else:
            self.admin_num = 0

        if (self.button['P']) and (self.admin):
            game.restart = True

        if self.button['A']:
            self.target_rotation -= self.rotation_speed
        if self.button['D']:
            self.target_rotation += self.rotation_speed


        # Поворачиваем к цели
        current_angle = math.degrees(math.atan2(self.direction.y, self.direction.x))
        angle_diff = (self.target_rotation - current_angle + 180) % 360 - 180

        if abs(angle_diff) > self.rotation_speed:
            angle_diff = math.copysign(self.rotation_speed, angle_diff)

        new_angle = current_angle + angle_diff
        self.direction = Vector2D(1, 0).rotate(new_angle)

        # Двигаемся
        self.position = self.position + self.direction * self.speed

        # Перезарядка
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if (self.shoot_cooldown <= 0) and (self.button['SPACE']):
            self.shoot_cooldown = self.max_shoot_cooldown
            return True

        return False

    def update_gold(self, gold):
        self.gold += gold
        k1 = 1 + self.gold / 200
        k2 = 1 + self.gold / 100
        self.max_health = Config.ship_health * k1
        self.shoot_damage = Config.ship_shoot_damage * k2
        self.health = min(self.health + gold, self.max_health)


    def destroy(self, list):
        try:
            if list is not None and self in list:
                list.remove(self)
        except Exception as e:
            print(f"Ошибка при удалении объекта: {e}")

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'type': 'ship',
            'direction_x': self.direction.x,
            'direction_y': self.direction.y,
            'health': self.health / self.max_health,
            'sid': self.sid,
            'admin': self.admin,
            'gold': self.gold
        })
        return data