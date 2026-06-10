from __future__ import annotations
import math
from dataclasses import dataclass


@dataclass
class Vec2:
    x: float
    y: float

    def __add__(self, other: Vec2) -> Vec2:
        return Vec2(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar: float) -> Vec2:
        return Vec2(self.x * scalar, self.y * scalar)

    def copy(self) -> Vec2:
        return Vec2(self.x, self.y)

    def magnitude(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalized(self) -> Vec2:
        m = self.magnitude()
        if m < 1e-12:
            raise ValueError("Cannot normalize zero vector")
        return Vec2(self.x / m, self.y / m)

    def angle(self) -> float:
        return math.atan2(self.y, self.x)
