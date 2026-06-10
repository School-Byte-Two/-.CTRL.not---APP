from __future__ import annotations
from dataclasses import dataclass, field
from smilefjes_bouncer.vec2 import Vec2


@dataclass
class TrailSegment:
    born_at: float
    pos: Vec2
    angle: float
    spread: float


@dataclass
class Smiley:
    smiley_id: int
    pos: Vec2
    vel: Vec2
    color: str
    trail: list = field(default_factory=list)   # list[TrailSegment]
    canvas_ids: list = field(default_factory=list)
