from objects.game_object import *
from objects.titan import Titan

class Drone(GameObject):
    def __init__(self, titan: Titan):
        import random
        super().__init__(titan.position, Config.drone_radius)
        self.team = titan.team
        self.radius = Config.drone_radius
        self.direction = Vector2D(1, 0).rotate(random.random() * 360)
        self.speed = Config.drone_speed
        self.rotation_speed = Config.drone_rotation_speed
        self.max_health = Config.drone_health
        self.health = Config.drone_health
        self.titan = titan
        self.target = None

        self.focus_time = 0
        self.max_focus_time = 13

        self.bullet_radius = Config.drone_bullet_radius
        self.shoot_damage = 10
        self.shoot_cooldown = 0
        self.max_shoot_cooldown = 10
        self.alive = True

    def get_rotate_to_obj(self, obj: GameObject) -> float:
        # Вычисляем вектор от дрона к цели
        direction_to_target = obj.position - self.position
        # Если цель находится в той же позиции - не нужно поворачивать
        if direction_to_target.length() == 0:
            return 0
        # Нормализуем вектор направления к цели
        direction_to_target = direction_to_target.normalized()
        # Вычисляем угол текущего направления дрона
        current_angle = math.degrees(math.atan2(self.direction.y, self.direction.x))
        # Вычисляем угол до цели
        target_angle = math.degrees(math.atan2(direction_to_target.y, direction_to_target.x))
        # Вычисляем разницу углов
        angle_diff = target_angle - current_angle
        # Приводим угол к диапазону (-180, 180] для минимального поворота
        angle_diff = (angle_diff + 180) % 360 - 180
        return angle_diff

    def update(self, enemies: list[GameObject]):
        if self.focus_time > 0:
            self.focus_time -= 1

        # Находим ближайшего врага
        if (not self.target) or (self.focus_time <= 0):
            closest = None
            closest_dist = float('inf')

            for enemy in enemies:
                distance = self.get_distance_to_obj(enemy) #(self.position - enemy.position).length()
                if distance < closest_dist:
                    closest_dist = distance
                    closest = enemy

            #print(self.position, closest.position, distance)
            self.target = closest
            self.focus_time = self.max_focus_time

        # Двигаемся к цели
        if self.target:
            direction_to_target = (self.target.position - self.position).norm().normalized()

            # Плавно поворачиваем к цели
            current_angle = math.degrees(math.atan2(self.direction.y, self.direction.x))
            target_angle = math.degrees(math.atan2(direction_to_target.y, direction_to_target.x))

            angle_diff = (target_angle - current_angle + 180) % 360 - 180

            if abs(angle_diff) > self.rotation_speed:
                angle_diff = math.copysign(self.rotation_speed, angle_diff)

            new_angle = current_angle + angle_diff
            self.direction = Vector2D(1, 0).rotate(new_angle)

        # Двигаемся
        self.position = self.position + self.direction * self.speed

        #ГЭНГ-БЭНГ
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        if self.shoot_cooldown <= 0:
            for enemy in enemies:
                if (self.get_distance_to_obj(enemy) < 200) \
                and (math.fabs(self.get_rotate_to_obj(enemy)) < 50):
                    self.shoot_cooldown = self.max_shoot_cooldown
                    return True

        return False


    def destroy(self, list):
        try:
            if list is not None and self in list:
                list.remove(self)
        except Exception as e:
            print(f"Ошибка при удалении объекта: {e}")

    def to_dict(self):
        data = super().to_dict()
        data.update({
            'type': 'drone',
            'health': self.health / self.max_health,
            'direction_x': self.direction.x,
            'direction_y': self.direction.y
        })
        return data