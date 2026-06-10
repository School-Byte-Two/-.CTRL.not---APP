from __future__ import annotations
import tkinter as tk
from smilefjes_bouncer.constants import CANVAS_W, CANVAS_H, INITIAL_SMILEYS
from smilefjes_bouncer.engine import AnimationEngine
from smilefjes_bouncer.panel import ControlPanel


class BouncerApp:
    def __init__(self, root: tk.Tk) -> None:
        self._root = root

        canvas = tk.Canvas(root, width=CANVAS_W, height=CANVAS_H, bg="black")
        canvas.pack(side=tk.LEFT)

        self._engine = AnimationEngine(canvas, width=CANVAS_W, height=CANVAS_H)

        for _ in range(INITIAL_SMILEYS):
            self._engine.add_smiley()

        panel = ControlPanel(root, self._engine, root)
        panel.pack(side=tk.RIGHT, fill=tk.Y)

        self._engine.start()

    def run(self) -> None:
        self._root.mainloop()
