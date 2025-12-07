"""
Tibia Pixel Bot - Overlay UI
Tibia-style dark overlay showing bot status, HP/Mana, and controls.
"""

import tkinter as tk
from tkinter import font as tkfont
import threading


class BotOverlay:
    """Tibia-style overlay window."""
    
    # Tibia color theme
    BG_COLOR = "#1a1a1a"  # Dark background
    BORDER_COLOR = "#3d3d3d"  # Border gray
    TEXT_COLOR = "#c0c0c0"  # Light gray text
    HP_COLOR = "#d44"  # Red for HP
    MANA_COLOR = "#48f"  # Blue for Mana
    ACCENT_COLOR = "#b8860b"  # Gold accent
    
    def __init__(self, on_start=None, on_stop=None):
        self.on_start = on_start
        self.on_stop = on_stop
        self.running = False
        self.bot_active = False
        
        self.root = None
        self.hp_var = None
        self.mana_var = None
        self.status_var = None
        self.btn_text = None
    
    def create_window(self):
        """Create the overlay window."""
        self.root = tk.Tk()
        self.root.title("Windify Bot")
        self.root.configure(bg=self.BG_COLOR)
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)
        
        # Remove window decorations for cleaner look (optional)
        # self.root.overrideredirect(True)
        
        # Main frame with border
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
            main_frame,
            text="🌀 Windify Bot",
            font=title_font,
            fg=self.ACCENT_COLOR,
            bg=self.BG_COLOR
        ).pack(pady=(0, 10))
        
        # Status section
        self.status_var = tk.StringVar(value="⏸️ Stopped")
        status_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        status_frame.pack(fill="x", pady=5)
        
        tk.Label(
            status_frame,
            text="Status:",
            fg=self.TEXT_COLOR,
            bg=self.BG_COLOR,
            width=8,
            anchor="w"
        ).pack(side="left")
        
        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            fg=self.TEXT_COLOR,
            bg=self.BG_COLOR,
            anchor="w"
        )
        self.status_label.pack(side="left", fill="x", expand=True)
        
        # Separator
        tk.Frame(main_frame, height=1, bg=self.BORDER_COLOR).pack(fill="x", pady=10)
        
        # HP display
        self.hp_var = tk.StringVar(value="---")
        hp_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        hp_frame.pack(fill="x", pady=3)
        
        tk.Label(
            hp_frame,
            text="❤️ HP:",
            fg=self.HP_COLOR,
            bg=self.BG_COLOR,
            width=8,
            anchor="w",
            font=("Helvetica", 12)
        ).pack(side="left")
        
        tk.Label(
            hp_frame,
            textvariable=self.hp_var,
            fg=self.HP_COLOR,
            bg=self.BG_COLOR,
            font=("Helvetica", 12, "bold"),
            anchor="e",
            width=8
        ).pack(side="right")
        
        # Mana display
        self.mana_var = tk.StringVar(value="---")
        mana_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        mana_frame.pack(fill="x", pady=3)
        
        tk.Label(
            mana_frame,
            text="🔷 Mana:",
            fg=self.MANA_COLOR,
            bg=self.BG_COLOR,
            width=8,
            anchor="w",
            font=("Helvetica", 12)
        ).pack(side="left")
        
        tk.Label(
            mana_frame,
            textvariable=self.mana_var,
            fg=self.MANA_COLOR,
            bg=self.BG_COLOR,
            font=("Helvetica", 12, "bold"),
            anchor="e",
            width=8
        ).pack(side="right")
        
        # Separator
        tk.Frame(main_frame, height=1, bg=self.BORDER_COLOR).pack(fill="x", pady=10)
        
        # Start/Stop button
        self.btn_text = tk.StringVar(value="▶️ Start")
        self.toggle_btn = tk.Button(
            main_frame,
            textvariable=self.btn_text,
            command=self._toggle_bot,
            bg="#2a2a2a",
            fg=self.ACCENT_COLOR,
            activebackground="#3a3a3a",
            activeforeground=self.ACCENT_COLOR,
            relief="flat",
            width=15,
            height=1,
            font=("Helvetica", 11, "bold"),
            cursor="hand2"
        )
        self.toggle_btn.pack(pady=5)
        
        # Position window in top-right corner
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        win_w = self.root.winfo_width()
        self.root.geometry(f"+{screen_w - win_w - 20}+50")
        
        self.running = True
    
    def _toggle_bot(self):
        """Toggle bot on/off."""
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
    
    def set_status(self, status: str):
        """Update status text."""
        if self.status_var:
            self.status_var.set(status)
    
    def set_hp(self, value: int):
        """Update HP display."""
        if self.hp_var:
            self.hp_var.set(f"{value:,}" if value else "---")
    
    def set_mana(self, value: int):
        """Update Mana display."""
        if self.mana_var:
            self.mana_var.set(f"{value:,}" if value else "---")
    
    def update(self):
        """Process pending UI events."""
        if self.root:
            self.root.update()
    
    def run(self):
        """Run the overlay main loop."""
        self.create_window()
        self.root.mainloop()
    
    def close(self):
        """Close the overlay."""
        self.running = False
        if self.root:
            self.root.destroy()


# Test the overlay
if __name__ == "__main__":
    import time
    import random
    
    overlay = BotOverlay()
    overlay.create_window()
    
    # Simulate updates
    for i in range(50):
        overlay.set_hp(random.randint(1000, 5000))
        overlay.set_mana(random.randint(500, 3000))
        overlay.set_status("✅ Running" if i % 2 == 0 else "🔍 Searching...")
        overlay.update()
        time.sleep(0.2)
    
    overlay.close()
