from __future__ import annotations
import tkinter as tk
from tkinter import messagebox, simpledialog
from smilefjes_bouncer.constants import SPEED_MAX, SPEED_MIN


class ControlPanel(tk.Frame):
    def __init__(self, parent: tk.Widget, engine, root: tk.Tk) -> None:
        super().__init__(parent, bg="#1e1e2e", padx=10, pady=10)
        self._engine = engine
        self._root = root
        self._selected_id = tk.StringVar()
        self._build_ui()

    def _build_ui(self) -> None:
        bg = "#1e1e2e"
        fg = "#cdd6f4"
        btn_bg = "#313244"
        btn_fg = "#cdd6f4"
        chaos_bg = "#f38ba8"

        def label(text, **kw):
            return tk.Label(self, text=text, bg=bg, fg=fg, **kw)

        def btn(text, cmd, color=btn_bg):
            return tk.Button(
                self, text=text, command=cmd,
                bg=color, fg=btn_fg,
                relief=tk.FLAT, padx=6, pady=4,
                activebackground="#45475a",
            )

        label("😊 Smiley Control", font=("Helvetica", 14, "bold")).pack(pady=(0, 12))

        btn("➕ Legg til smiley", self._add).pack(fill=tk.X, pady=2)
        btn("➖ Fjern siste", self._remove_last).pack(fill=tk.X, pady=2)

        # ── Select smiley ────────────────────────────────────────────────────
        frame = tk.LabelFrame(self, text="Velg smiley", bg=bg, fg=fg, padx=6, pady=6)
        frame.pack(fill=tk.X, pady=8)

        self._id_menu = tk.OptionMenu(frame, self._selected_id, "")
        self._id_menu.config(bg=btn_bg, fg=btn_fg, highlightthickness=0)
        self._id_menu.pack(fill=tk.X)

        btn("🎲 Tilfeldig retning", self._randomize_dir).pack(fill=tk.X, pady=2)
        btn("🗑  Fjern valgt", self._remove_selected).pack(fill=tk.X, pady=2)

        # ── Speed ────────────────────────────────────────────────────────────
        sf = tk.LabelFrame(self, text="Hastighet (alle)", bg=bg, fg=fg, padx=6, pady=6)
        sf.pack(fill=tk.X, pady=8)

        self._speed_var = tk.DoubleVar(value=3.5)
        scale = tk.Scale(
            sf, from_=SPEED_MIN, to=SPEED_MAX,
            resolution=0.5, orient=tk.HORIZONTAL,
            variable=self._speed_var,
            command=self._on_speed,
            bg=bg, fg=fg, troughcolor=btn_bg,
            highlightthickness=0,
        )
        scale.pack(fill=tk.X)

        # ── Bottom buttons ───────────────────────────────────────────────────
        btn("💥 CHAOS 🔥", self._confirm_chaos, color=chaos_bg).pack(fill=tk.X, pady=(12, 2))
        btn("🚪 Avslutt", self._quit).pack(fill=tk.X, pady=2)

        self._refresh_smiley_list()

    # ── Callbacks ────────────────────────────────────────────────────────────

    def _add(self) -> None:
        self._engine.add_smiley()
        self._refresh_smiley_list()

    def _remove_last(self) -> None:
        self._engine.remove_last_smiley()
        self._refresh_smiley_list()

    def _remove_selected(self) -> None:
        val = self._selected_id.get()
        if val and val.isdigit():
            self._engine.remove_smiley(int(val))
            self._refresh_smiley_list()

    def _randomize_dir(self) -> None:
        val = self._selected_id.get()
        if val and val.isdigit():
            self._engine.randomize_direction(int(val))

    def _on_speed(self, _=None) -> None:
        self._engine.set_global_speed(self._speed_var.get())

    def _confirm_chaos(self) -> None:
        if messagebox.askyesno(
            "CHAOS 🔥",
            "Dette spawner masse smilefjes og slår AV PC-en om 3 sekunder.\n\nEr du HELT sikker?",
        ):
            self._engine.trigger_chaos()
            self._refresh_smiley_list()

    def _quit(self) -> None:
        self._engine.stop()
        self._root.destroy()

    def _refresh_smiley_list(self) -> None:
        ids = self._engine.smiley_ids()
        menu = self._id_menu["menu"]
        menu.delete(0, tk.END)
        for sid in ids:
            menu.add_command(
                label=str(sid),
                command=lambda v=str(sid): self._selected_id.set(v),
            )
        if ids:
            if self._selected_id.get() not in [str(i) for i in ids]:
                self._selected_id.set(str(ids[-1]))
        else:
            self._selected_id.set("")
