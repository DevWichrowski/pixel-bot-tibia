"""
Windify Bot - Overlay UI
Tibia-style dark overlay with status, HP/Mana, and heal controls.
"""

import tkinter as tk
from tkinter import font as tkfont
import threading


class BotOverlay:
    """Tibia-style overlay window."""
    
    # Tibia color theme
    BG_COLOR = "#1a1a1a"
    BORDER_COLOR = "#3d3d3d"
    TEXT_COLOR = "#c0c0c0"
    HP_COLOR = "#d44"
    MANA_COLOR = "#48f"
    ACCENT_COLOR = "#b8860b"
    SUCCESS_COLOR = "#4a4"
    
    def __init__(self, on_start=None, on_stop=None):
        self.on_start = on_start
        self.on_stop = on_stop
        self.running = False
        self.bot_active = False
        
        # Callbacks for healer
        self.on_heal_toggle = None
        self.on_critical_toggle = None
        self.on_heal_threshold_change = None
        self.on_critical_threshold_change = None
        self.on_max_hp_change = None
        
        self.root = None
        self.hp_var = None
        self.mana_var = None
        self.status_var = None
        self.btn_text = None
        self.max_hp_var = None
        self.heal_enabled = None
        self.critical_enabled = None
        self.heal_threshold_var = None
        self.critical_threshold_var = None
    
    def create_window(self):
        """Create the overlay window."""
        self.root = tk.Tk()
        self.root.title("Windify Bot")
        self.root.configure(bg=self.BG_COLOR)
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)
        
        # Main frame
        main_frame = tk.Frame(
            self.root, 
            bg=self.BG_COLOR, 
            highlightbackground=self.BORDER_COLOR,
            highlightthickness=2,
            padx=15, 
            pady=10
        )
        main_frame.pack(fill="both", expand=True)
        
        # Title
        title_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
        tk.Label(
            main_frame, text="🌀 Windify Bot",
            font=title_font, fg=self.ACCENT_COLOR, bg=self.BG_COLOR
        ).pack(pady=(0, 10))
        
        # Status
        self.status_var = tk.StringVar(value="⏸️ Stopped")
        status_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        status_frame.pack(fill="x", pady=5)
        tk.Label(status_frame, text="Status:", fg=self.TEXT_COLOR, bg=self.BG_COLOR, width=8, anchor="w").pack(side="left")
        tk.Label(status_frame, textvariable=self.status_var, fg=self.TEXT_COLOR, bg=self.BG_COLOR).pack(side="left")
        
        self._add_separator(main_frame)
        
        # HP display
        self.hp_var = tk.StringVar(value="---")
        hp_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        hp_frame.pack(fill="x", pady=3)
        tk.Label(hp_frame, text="❤️ HP:", fg=self.HP_COLOR, bg=self.BG_COLOR, width=8, anchor="w", font=("Helvetica", 12)).pack(side="left")
        tk.Label(hp_frame, textvariable=self.hp_var, fg=self.HP_COLOR, bg=self.BG_COLOR, font=("Helvetica", 12, "bold"), width=8, anchor="e").pack(side="right")
        
        # Max HP input
        max_hp_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        max_hp_frame.pack(fill="x", pady=2)
        tk.Label(max_hp_frame, text="Max HP:", fg=self.TEXT_COLOR, bg=self.BG_COLOR, width=8, anchor="w").pack(side="left")
        self.max_hp_var = tk.StringVar(value="---")
        max_hp_entry = tk.Entry(max_hp_frame, textvariable=self.max_hp_var, width=8, bg="#2a2a2a", fg=self.TEXT_COLOR, insertbackground=self.TEXT_COLOR)
        max_hp_entry.pack(side="right")
        max_hp_entry.bind("<Return>", self._on_max_hp_change)
        
        # Mana display
        self.mana_var = tk.StringVar(value="---")
        mana_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        mana_frame.pack(fill="x", pady=3)
        tk.Label(mana_frame, text="🔷 Mana:", fg=self.MANA_COLOR, bg=self.BG_COLOR, width=8, anchor="w", font=("Helvetica", 12)).pack(side="left")
        tk.Label(mana_frame, textvariable=self.mana_var, fg=self.MANA_COLOR, bg=self.BG_COLOR, font=("Helvetica", 12, "bold"), width=8, anchor="e").pack(side="right")
        
        self._add_separator(main_frame)
        
        # Heal section
        tk.Label(main_frame, text="Auto Heal", fg=self.ACCENT_COLOR, bg=self.BG_COLOR, font=("Helvetica", 11, "bold")).pack(pady=(5, 3))
        
        # Normal Heal toggle
        self.heal_enabled = tk.BooleanVar(value=False)
        self.heal_threshold_var = tk.StringVar(value="75")
        heal_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        heal_frame.pack(fill="x", pady=2)
        tk.Checkbutton(
            heal_frame, text="Heal (F1)", variable=self.heal_enabled,
            command=self._on_heal_toggle, bg=self.BG_COLOR, fg=self.TEXT_COLOR,
            selectcolor="#2a2a2a", activebackground=self.BG_COLOR
        ).pack(side="left")
        tk.Label(heal_frame, text="@", fg=self.TEXT_COLOR, bg=self.BG_COLOR).pack(side="left", padx=5)
        heal_entry = tk.Entry(heal_frame, textvariable=self.heal_threshold_var, width=4, bg="#2a2a2a", fg=self.TEXT_COLOR, insertbackground=self.TEXT_COLOR)
        heal_entry.pack(side="left")
        heal_entry.bind("<Return>", self._on_heal_threshold_change)
        tk.Label(heal_frame, text="%", fg=self.TEXT_COLOR, bg=self.BG_COLOR).pack(side="left")
        
        # Critical Heal toggle
        self.critical_enabled = tk.BooleanVar(value=False)
        self.critical_threshold_var = tk.StringVar(value="50")
        crit_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        crit_frame.pack(fill="x", pady=2)
        tk.Checkbutton(
            crit_frame, text="Critical (F2)", variable=self.critical_enabled,
            command=self._on_critical_toggle, bg=self.BG_COLOR, fg=self.HP_COLOR,
            selectcolor="#2a2a2a", activebackground=self.BG_COLOR
        ).pack(side="left")
        tk.Label(crit_frame, text="@", fg=self.TEXT_COLOR, bg=self.BG_COLOR).pack(side="left", padx=5)
        crit_entry = tk.Entry(crit_frame, textvariable=self.critical_threshold_var, width=4, bg="#2a2a2a", fg=self.TEXT_COLOR, insertbackground=self.TEXT_COLOR)
        crit_entry.pack(side="left")
        crit_entry.bind("<Return>", self._on_critical_threshold_change)
        tk.Label(crit_frame, text="%", fg=self.TEXT_COLOR, bg=self.BG_COLOR).pack(side="left")
        
        self._add_separator(main_frame)
        
        # Start/Stop button
        self.btn_text = tk.StringVar(value="▶️ Start")
        self.toggle_btn = tk.Button(
            main_frame, textvariable=self.btn_text, command=self._toggle_bot,
            bg="#2a2a2a", fg=self.ACCENT_COLOR, activebackground="#3a3a3a",
            activeforeground=self.ACCENT_COLOR, relief="flat", width=15,
            font=("Helvetica", 11, "bold"), cursor="hand2"
        )
        self.toggle_btn.pack(pady=5)
        
        # Position window
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        win_w = self.root.winfo_width()
        self.root.geometry(f"+{screen_w - win_w - 20}+50")
        
        self.running = True
    
    def _add_separator(self, parent):
        tk.Frame(parent, height=1, bg=self.BORDER_COLOR).pack(fill="x", pady=8)
    
    def _toggle_bot(self):
        if self.bot_active:
            self.bot_active = False
            self.btn_text.set("▶️ Start")
            self.set_status("⏸️ Stopped")
            if self.on_stop:
                self.on_stop()
        else:
            self.bot_active = True
            self.btn_text.set("⏹️ Stop")
            self.set_status("🔍 Searching...")
            if self.on_start:
                self.on_start()
    
    def _on_heal_toggle(self):
        if self.on_heal_toggle:
            self.on_heal_toggle(self.heal_enabled.get())
    
    def _on_critical_toggle(self):
        if self.on_critical_toggle:
            self.on_critical_toggle(self.critical_enabled.get())
    
    def _on_heal_threshold_change(self, event=None):
        try:
            val = int(self.heal_threshold_var.get())
            if self.on_heal_threshold_change:
                self.on_heal_threshold_change(val)
        except ValueError:
            pass
    
    def _on_critical_threshold_change(self, event=None):
        try:
            val = int(self.critical_threshold_var.get())
            if self.on_critical_threshold_change:
                self.on_critical_threshold_change(val)
        except ValueError:
            pass
    
    def _on_max_hp_change(self, event=None):
        try:
            val = int(self.max_hp_var.get())
            if self.on_max_hp_change:
                self.on_max_hp_change(val)
        except ValueError:
            pass
    
    def set_status(self, status: str):
        if self.status_var:
            self.status_var.set(status)
    
    def set_hp(self, value: int):
        if self.hp_var:
            self.hp_var.set(f"{value:,}" if value else "---")
    
    def set_mana(self, value: int):
        if self.mana_var:
            self.mana_var.set(f"{value:,}" if value else "---")
    
    def set_max_hp(self, value: int):
        if self.max_hp_var and value:
            self.max_hp_var.set(str(value))
    
    def update(self):
        if self.root:
            self.root.update()
    
    def run(self):
        self.create_window()
        self.root.mainloop()
    
    def close(self):
        self.running = False
        if self.root:
            self.root.destroy()


if __name__ == "__main__":
    overlay = BotOverlay()
    overlay.run()
