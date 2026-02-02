import math
from dataclasses import dataclass


from config import *


def norm_value(value, size=4000):
    value = value % size
    if value > size / 2:
        value -= size
    elif value < -size / 2:
        value += size
    return value



@dataclass
class Vector2D:
    x: float
    y: float

    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)

    def norm(self):
        return Vector2D(norm_value(self.x), norm_value(self.y))

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalized(self):
        length = self.length()
        if length == 0:
            return Vector2D(0, 0)
        return Vector2D(self.x / length, self.y / length)

    def rotate(self, angle_deg):
        angle_rad = math.radians(angle_deg)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        return Vector2D(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a
        )


class GameObject:
    def __init__(self, position: Vector2D, radius: float):
        self.position = position
        self.radius = radius

    def norm_position(self):
        width = Config.width
        height = Config.height
        if self.position.x < 0:
            self.position.x += width
        elif self.position.x > width:
            self.position.x -= width
        if self.position.y < 0:
            self.position.y += height
        elif self.position.y > height:
            self.position.y -= height

    def collides_with(self, other: 'GameObject') -> bool:
        distance = Vector2D(
            norm_value(self.position.x - other.position.x),
            norm_value(self.position.y - other.position.y)
        ).length()
        return distance < (self.radius + other.radius)

    def get_distance_to_obj(self, obj):
        x1 = self.position.x - obj.position.x
        y1 = self.position.y - obj.position.y
        x = norm_value(self.position.x - obj.position.x)
        y = norm_value(self.position.y - obj.position.y)
        distance = Vector2D(x, y).length()
        if distance > math.sqrt(2) * 2000:
            print('distance:', distance, self.position, obj.position)
            print(x1, y1, '\n', x, y)
        return distance - self.radius - obj.radius

    def to_dict(self):
        return {
            'x': self.position.x,
            'y': self.position.y,
            'radius': self.radius
        }