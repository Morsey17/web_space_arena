import random
import time
import math

class GameObject:
    def __init__(self, x, y, radius=0):
        self.x = x
        self.y = y
        self.radius = radius