from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import math
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple
import time

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
    def __init__(self, id: str, position: Vector2D, team: str):
        self.id = id
        self.position = position
        self.team = team  # "red" или "blue"
        self.radius = 10
        self.alive = True

    def collides_with(self, other: 'GameObject') -> bool:
        distance = (self.position - other.position).length()
        return distance < (self.radius + other.radius)

    def to_dict(self):
        return {
            'id': self.id,
            'x': self.position.x,
            'y': self.position.y,
            'team': self.team,
            'radius': self.radius,
            'alive': self.alive
        }