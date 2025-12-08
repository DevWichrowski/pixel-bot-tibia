"""
Windify Helper - Tibia-Style Overlay UI
Pixel art styled overlay with Status and Config tabs.
"""

import tkinter as tk
from tkinter import font as tkfont
from typing import Callable, Optional
from region_selector import RegionSelector, Region


class TibiaStyleOverlay:
    """Tibia pixel art styled overlay with tabbed interface."""
    
    # Tibia Pixel Art Theme
    THEME = {
        # Base colors
        "bg": "#2d2d2d",
        "bg_dark": "#1a1a1a",
        "bg_light": "#3a3a3a",
        
        # 3D Bevel borders
        "border_light": "#4a4a4a",
        "border_dark": "#151515",
        
        # Text colors
        "text": "#c0c0c0",
        "text_dim": "#808080",
        "text_bright": "#ffffff",
        
        # Status colors
        "hp": "#c54444",
        "hp_bg": "#3a2020",
        "mana": "#4488ff",
        "mana_bg": "#202838",
        
        # Accent
        "accent": "#b8860b",
        "accent_bright": "#daa520",
        "success": "#4a9944",
        "error": "#c54444",
        
        # Tab colors
        "tab_active": "#3a3a3a",
        "tab_inactive": "#252525",
        
        # Extra features
        "extra": "#b044c5",
    }
    
    def __init__(self):
        self.root: Optional[tk.Tk] = None
        self.running = False
        self.bot_active = False
        
        # Callbacks
        self.on_start: Optional[Callable] = None
        self.on_stop: Optional[Callable] = None
        self.on_hp_region_select: Optional[Callable] = None
        self.on_mana_region_select: Optional[Callable] = None
        self.on_reset_config: Optional[Callable] = None
        
        # Healer callbacks
        self.on_heal_toggle: Optional[Callable[[bool], None]] = None
        self.on_critical_toggle: Optional[Callable[[bool], None]] = None
        self.on_mana_toggle: Optional[Callable[[bool], None]] = None
        self.on_heal_threshold_change: Optional[Callable[[int], None]] = None
        self.on_critical_threshold_change: Optional[Callable[[int], None]] = None
        self.on_mana_threshold_change: Optional[Callable[[int], None]] = None
        
        # Hotkey change callbacks
        self.on_heal_hotkey_change: Optional[Callable[[str], None]] = None
        self.on_critical_hotkey_change: Optional[Callable[[str], None]] = None
        self.on_mana_hotkey_change: Optional[Callable[[str], None]] = None
        
        # Auto Eater callbacks
        self.on_eater_toggle: Optional[Callable[[bool], None]] = None
        self.on_food_type_change: Optional[Callable[[str], None]] = None
        self.on_eater_hotkey_change: Optional[Callable[[str], None]] = None
        
        # Auto Haste callbacks
        self.on_haste_toggle: Optional[Callable[[bool], None]] = None
        self.on_haste_hotkey_change: Optional[Callable[[str], None]] = None
        
        # Auto Skinner callbacks
        self.on_skinner_toggle: Optional[Callable[[bool], None]] = None
        self.on_skinner_hotkey_change: Optional[Callable[[str], None]] = None
        
        # UI variables
        self.status_var: Optional[tk.StringVar] = None
        self.hp_var: Optional[tk.StringVar] = None
        self.mana_var: Optional[tk.StringVar] = None
        self.hp_region_status: Optional[tk.StringVar] = None
        self.mana_region_status: Optional[tk.StringVar] = None
        
        # Tab state
        self.current_tab = "status"
        self.tab_frames = {}
        self.tab_buttons = {}
        
        # Healer vars
        self.heal_enabled = None
        self.critical_enabled = None
        self.mana_enabled = None
        self.heal_threshold_var = None
        self.critical_threshold_var = None
        self.mana_threshold_var = None
        
        # Eater vars
        self.eater_enabled = None
        self.food_type_var = None
        self.eater_hotkey_var = None
        
        # Haste vars
        self.haste_enabled = None
        self.haste_hotkey_var = None
        
        # Skinner vars
        self.skinner_enabled = None
        self.skinner_hotkey_var = None
        
        # Region selector
        self.region_selector = RegionSelector()
        
        # Config state
        self.hp_region_configured = False
        self.mana_region_configured = False
        
        # Start button reference
        self.start_btn: Optional[tk.Button] = None
        self.entries = []
        
        # Error label
        self.error_var = None
        self.error_label = None
        
        # Hotkey vars
        self.heal_hotkey_var = None
        self.critical_hotkey_var = None
        self.mana_hotkey_var = None
        
        # Key capture state
        self._capturing_hotkey = False
        self._capture_callback = None
    
    def create_window(self):
        """Create the overlay window."""
        self.root = tk.Tk()
        self.root.title("Tibia Bot Overlay")
        
        # Always on top
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)  # No window border
        self.root.configure(bg=self.THEME["bg"])
        
        # Initial size and position (top-left)
        self.root.geometry("260x520+20+100")  # Increased height for new features
        
        # Initialize shared UI variables here (so they are available for all tabs)
        self.eater_hotkey_var = tk.StringVar(value="]")
        self.haste_hotkey_var = tk.StringVar(value="x")
        self.skinner_hotkey_var = tk.StringVar(value="[")
        self.heal_hotkey_var = tk.StringVar(value="F1")
        self.critical_hotkey_var = tk.StringVar(value="F2")
        self.mana_hotkey_var = tk.StringVar(value="F4")
        
        # Main Frame with border
        main_frame = tk.Frame(
            self.root, 
            bg=self.THEME["bg"],
            highlightbackground=self.THEME["border_light"], # Changed from "border" to "border_light" to match theme
            highlightthickness=1
        )
        main_frame.pack(fill="both", expand=True)
        
        # Header (Draggable)
        self._create_header(main_frame)
        
        # Tab Buttons
        self._create_tabs(main_frame)
        
        # Content Area
        self.content_frame = tk.Frame(main_frame, bg=self.THEME["bg"])
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create tabs content
        self._create_status_tab()
        self._create_config_tab()
        
        # Show default tab
        self._show_tab("status")
        
        self.running = True # Added this line as it was in the original create_window
    
    def _create_header(self, parent):
        """Create header with drag functionality."""
        header = tk.Frame(parent, bg=self.THEME["bg_dark"], height=28)
        header.pack(fill="x")
        
        # Title
        title_label = tk.Label(
            header, 
            text="Windify Bot", 
            font=("Courier", 10, "bold"),
            fg=self.THEME["accent"],
            bg=self.THEME["bg_dark"]
        )
        title_label.pack(side="left", padx=8)
        
        # Close button
        close_btn = tk.Button(
            header,
            text="✕",
            font=("Arial", 9),
            fg=self.THEME["text_dim"],
            bg=self.THEME["bg_dark"],
            activebackground=self.THEME["error"],
            activeforeground="white",
            relief="flat",
            bd=0,
            command=self.root.destroy,
            width=3
        )
        close_btn.pack(side="right")
        
        # Drag logic
        def start_move(event):
            self.root.x = event.x
            self.root.y = event.y

        def stop_move(event):
            self.root.x = None
            self.root.y = None

        def do_move(event):
            deltax = event.x - self.root.x
            deltay = event.y - self.root.y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")

        header.bind("<ButtonPress-1>", start_move)
        header.bind("<ButtonRelease-1>", stop_move)
        header.bind("<B1-Motion>", do_move)
        title_label.bind("<ButtonPress-1>", start_move)
        title_label.bind("<ButtonRelease-1>", stop_move)
        title_label.bind("<B1-Motion>", do_move)

    def _create_tabs(self, parent):
        """Create navigation tabs."""
        tabs_frame = tk.Frame(parent, bg=self.THEME["bg"])
        tabs_frame.pack(fill="x", pady=5)
        
        # Status Tab Button
        self.tab_buttons["status"] = tk.Button(
            tabs_frame,
            text="STATUS",
            font=("Courier", 9, "bold"),
            fg=self.THEME["text"],
            bg=self.THEME["bg"],
            relief="flat",
            command=lambda: self._show_tab("status"),
            width=10
        )
        self.tab_buttons["status"].pack(side="left", padx=5)
        
        # Config Tab Button
        self.tab_buttons["config"] = tk.Button(
            tabs_frame,
            text="CONFIG",
            font=("Courier", 9, "bold"),
            fg=self.THEME["text_dim"],  # Inactive
            bg=self.THEME["bg"],
            relief="flat",
            command=lambda: self._show_tab("config"),
            width=10
        )
        self.tab_buttons["config"].pack(side="left", padx=5)
        
        # Separator
        tk.Frame(parent, height=1, bg=self.THEME["border_dark"]).pack(fill="x")
    
    def _show_tab(self, tab_id: str):
        """Switch to specified tab."""
        self.current_tab = tab_id
        
        # Update button styles
        for name, btn in self.tab_buttons.items():
            if name == tab_id:
                btn.configure(fg=self.THEME["accent"])
            else:
                btn.configure(fg=self.THEME["text_dim"])
        
        # Show/hide frames
        for tid, frame in self.tab_frames.items():
            if tid == tab_id:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()
    
    def _create_status_tab(self):
        """Create Status tab content."""
        frame = tk.Frame(self.content_frame, bg=self.THEME["bg"])
        self.tab_frames["status"] = frame
        
        # Status Label
        self.status_var = tk.StringVar(value="Waiting...")
        status_lbl = tk.Label(
            frame, 
            textvariable=self.status_var,
            font=("Courier", 10),
            fg=self.THEME["text"],
            bg=self.THEME["bg"]
        )
        status_lbl.pack(pady=5)
        
        self._add_separator(frame)
        
        # HP Display
        hp_frame = tk.Frame(frame, bg=self.THEME["bg"])
        hp_frame.pack(fill="x", pady=2)
        tk.Label(hp_frame, text="HP:", font=("Courier", 10, "bold"), fg=self.THEME["hp"], bg=self.THEME["bg"], width=5, anchor="w").pack(side="left")
        self.hp_var = tk.StringVar(value="--- / ---")
        tk.Label(hp_frame, textvariable=self.hp_var, font=("Courier", 10), fg=self.THEME["text_bright"], bg=self.THEME["bg"]).pack(side="right")
        
        # Mana Display
        mana_frame = tk.Frame(frame, bg=self.THEME["bg"])
        mana_frame.pack(fill="x", pady=2)
        tk.Label(mana_frame, text="MP:", font=("Courier", 10, "bold"), fg=self.THEME["mana"], bg=self.THEME["bg"], width=5, anchor="w").pack(side="left")
        self.mana_var = tk.StringVar(value="--- / ---")
        tk.Label(mana_frame, textvariable=self.mana_var, font=("Courier", 10), fg=self.THEME["text_bright"], bg=self.THEME["bg"]).pack(side="right")
        
        self._add_separator(frame)
        
        # Controls Header
        tk.Label(
            frame,
            text="Controls",
            font=("Courier", 10, "bold"),
            fg=self.THEME["accent"],
            bg=self.THEME["bg"]
        ).pack(pady=(5, 5))
        
        # Heal toggle
        self.heal_enabled = tk.BooleanVar(value=True)
        self.heal_threshold_var = tk.StringVar(value="75")
        self._create_heal_row(frame, "Heal (F1)", self.heal_enabled, self.heal_threshold_var, 
                              self._on_heal_toggle, self._on_heal_threshold_change, self.THEME["hp"])
        
        # Critical heal toggle
        self.critical_enabled = tk.BooleanVar(value=True)
        self.critical_threshold_var = tk.StringVar(value="50")
        self._create_heal_row(frame, "Crit (F2)", self.critical_enabled, self.critical_threshold_var,
                              self._on_critical_toggle, self._on_critical_threshold_change, self.THEME["error"])
        
        # Mana toggle
        self.mana_enabled = tk.BooleanVar(value=True)
        self.mana_threshold_var = tk.StringVar(value="60")
        self._create_heal_row(frame, "Mana (F4)", self.mana_enabled, self.mana_threshold_var,
                              self._on_mana_toggle, self._on_mana_threshold_change, self.THEME["mana"])
        
        # Auto Eater toggle
        self.eater_enabled = tk.BooleanVar(value=False)
        self._create_simple_toggle(frame, "Auto Eater", self.eater_enabled, self._on_eater_toggle, self.THEME["accent_bright"], self.eater_hotkey_var)
        
        # Auto Haste toggle
        self.haste_enabled = tk.BooleanVar(value=False)
        self._create_simple_toggle(frame, "Auto Haste", self.haste_enabled, self._on_haste_toggle, self.THEME["extra"], self.haste_hotkey_var)
        
        # Auto Skinner toggle
        self.skinner_enabled = tk.BooleanVar(value=False)
        self._create_simple_toggle(frame, "Auto Skinner", self.skinner_enabled, self._on_skinner_toggle, self.THEME["accent"], self.skinner_hotkey_var)
        
        self._add_separator(frame)
        
        # Start/Stop button
        self.start_btn = tk.Button(
            frame,
            text="▶️ Start",
            font=("Courier", 11, "bold"),
            fg=self.THEME["accent_bright"],
            bg=self.THEME["bg_light"],
            activebackground=self.THEME["bg"],
            activeforeground=self.THEME["accent_bright"],
            relief="flat",
            cursor="hand2",
            width=18,
            command=self._toggle_bot
        )
        self.start_btn.pack(pady=8)
        
        # Error message label (hidden by default)
        self.error_var = tk.StringVar(value="")
        self.error_label = tk.Label(
            frame,
            textvariable=self.error_var,
            font=("Courier", 9),
            fg=self.THEME["error"],
            bg=self.THEME["bg"]
        )
    
    def _create_simple_toggle(self, parent, label, enabled_var, toggle_cmd, color, hotkey_var=None):
        """Create a simple toggle row (optional hotkey display)."""
        row = tk.Frame(parent, bg=self.THEME["bg"])
        row.pack(fill="x", pady=2)
        
        cb = tk.Checkbutton(
            row,
            text=label,
            variable=enabled_var,
            command=toggle_cmd,
            font=("Courier", 10),
            fg=color,
            bg=self.THEME["bg"],
            selectcolor=self.THEME["bg_dark"],
            activebackground=self.THEME["bg"]
        )
        cb.pack(side="left")
        
        if hotkey_var:
            def update_label(*args):
                cb.config(text=f"{label} ({hotkey_var.get()})")
            
            # Initial set
            update_label()
            
            # Update on change
            hotkey_var.trace_add("write", update_label)
    
    def _create_heal_row(self, parent, label, enabled_var, threshold_var, toggle_cmd, threshold_cmd, color):
        """Create a heal toggle row."""
        row = tk.Frame(parent, bg=self.THEME["bg"])
        row.pack(fill="x", pady=2)
        
        cb = tk.Checkbutton(
            row,
            text=label,
            variable=enabled_var,
            command=toggle_cmd,
            font=("Courier", 10),
            fg=color,
            bg=self.THEME["bg"],
            selectcolor=self.THEME["bg_dark"],
            activebackground=self.THEME["bg"]
        )
        cb.pack(side="left")
        
        tk.Label(row, text="@", fg=self.THEME["text_dim"], bg=self.THEME["bg"]).pack(side="left", padx=3)
        
        entry = tk.Entry(
            row,
            textvariable=threshold_var,
            width=4,
            font=("Courier", 10),
            fg=self.THEME["text"],
            bg=self.THEME["bg_dark"],
            insertbackground=self.THEME["text"],
            relief="flat"
        )
        entry.pack(side="left")
        entry.bind("<Return>", threshold_cmd)
        entry.bind("<FocusOut>", threshold_cmd)  # Also save on click away
        self.entries.append(entry)
        
        tk.Label(row, text="%", fg=self.THEME["text_dim"], bg=self.THEME["bg"]).pack(side="left")
    
    def _create_config_tab(self):
        """Create Config tab content."""
        frame = tk.Frame(self.content_frame, bg=self.THEME["bg"])
        self.tab_frames["config"] = frame
        
        # Title
        tk.Label(
            frame,
            text="Region Configuration",
            font=("Courier", 10, "bold"),
            fg=self.THEME["accent"],
            bg=self.THEME["bg"]
        ).pack(pady=(5, 10))
        
        # HP Region
        hp_box = tk.Frame(frame, bg=self.THEME["bg"])
        hp_box.pack(fill="x", pady=5)
        
        hp_row = tk.Frame(hp_box, bg=self.THEME["bg"])
        hp_row.pack(fill="x")
        tk.Label(hp_row, text="HP Region:", font=("Courier", 10), fg=self.THEME["text"], bg=self.THEME["bg"], width=12, anchor="w").pack(side="left", padx=5)
        tk.Button(hp_row, text="📍 Select", font=("Courier", 9), fg=self.THEME["text_bright"], bg=self.THEME["bg_light"], relief="flat", cursor="hand2", command=self._select_hp_region).pack(side="right", padx=5)
        
        self.hp_region_status = tk.StringVar(value="✗ Not configured")
        tk.Label(hp_box, textvariable=self.hp_region_status, font=("Courier", 9), fg=self.THEME["text_dim"], bg=self.THEME["bg"]).pack(anchor="w", padx=10)
        
        # Mana Region
        mana_box = tk.Frame(frame, bg=self.THEME["bg"])
        mana_box.pack(fill="x", pady=5)
        
        mana_row = tk.Frame(mana_box, bg=self.THEME["bg"])
        mana_row.pack(fill="x")
        tk.Label(mana_row, text="Mana Region:", font=("Courier", 10), fg=self.THEME["text"], bg=self.THEME["bg"], width=12, anchor="w").pack(side="left", padx=5)
        tk.Button(mana_row, text="📍 Select", font=("Courier", 9), fg=self.THEME["text_bright"], bg=self.THEME["bg_light"], relief="flat", cursor="hand2", command=self._select_mana_region).pack(side="right", padx=5)
        
        self.mana_region_status = tk.StringVar(value="✗ Not configured")
        tk.Label(mana_box, textvariable=self.mana_region_status, font=("Courier", 9), fg=self.THEME["text_dim"], bg=self.THEME["bg"]).pack(anchor="w", padx=10)
        
        self._add_separator(frame)
        
        # Auto Eater Config
        tk.Label(
            frame,
            text="Food Configuration",
            font=("Courier", 10, "bold"),
            fg=self.THEME["accent"],
            bg=self.THEME["bg"]
        ).pack(pady=(5, 8))
        
        # Food Type Dropdown (simulated with OptionMenu)
        food_row = tk.Frame(frame, bg=self.THEME["bg"])
        food_row.pack(fill="x", pady=2, padx=5)
        tk.Label(food_row, text="Food Type:", font=("Courier", 10), fg=self.THEME["text"], bg=self.THEME["bg"], width=10, anchor="w").pack(side="left")
        
        self.food_type_var = tk.StringVar(value="fire_mushroom")
        food_options = ["fire_mushroom", "brown_mushroom"]
        
        # Custom styling for OptionMenu is tricky in Tkinter, using basic for now
        om = tk.OptionMenu(food_row, self.food_type_var, *food_options, command=self._on_food_type_change)
        om.configure(bg=self.THEME["bg_dark"], fg=self.THEME["text"], highlightthickness=0, relief="flat", width=15)
        om["menu"].config(bg=self.THEME["bg_dark"], fg=self.THEME["text"])
        om.pack(side="left", padx=5)
        
        # Eater Hotkey
        self._create_hotkey_row(frame, "Food Key:", self.eater_hotkey_var, "eater")

        self._add_separator(frame)

        # Auto Haste Config
        tk.Label(
            frame,
            text="Haste Configuration",
            font=("Courier", 10, "bold"),
            fg=self.THEME["accent"],
            bg=self.THEME["bg"]
        ).pack(pady=(5, 8))
        
        # Haste Hotkey
        self._create_hotkey_row(frame, "Haste Key:", self.haste_hotkey_var, "haste")
        
        # Skinner Hotkey
        self._create_hotkey_row(frame, "Skin Key:", self.skinner_hotkey_var, "skinner")
        
        self._add_separator(frame)
        
        # Hotkeys Section
        tk.Label(
            frame,
            text="Heal Hotkeys",
            font=("Courier", 10, "bold"),
            fg=self.THEME["accent"],
            bg=self.THEME["bg"]
        ).pack(pady=(5, 8))
        
        # Heal hotkey
        self._create_hotkey_row(frame, "Heal:", self.heal_hotkey_var, "heal")
        
        # Critical heal hotkey
        self._create_hotkey_row(frame, "Critical:", self.critical_hotkey_var, "critical")
        
        # Mana hotkey
        self._create_hotkey_row(frame, "Mana:", self.mana_hotkey_var, "mana")
        
        self._add_separator(frame)
        
        # Reset button
        tk.Button(
            frame,
            text="🔄 Reset All",
            font=("Courier", 10),
            fg=self.THEME["error"],
            bg=self.THEME["bg_light"],
            activebackground=self.THEME["bg_dark"],
            relief="flat",
            cursor="hand2",
            command=self._reset_config
        ).pack(pady=8)
    
    def _create_hotkey_row(self, parent, label: str, var: tk.StringVar, hotkey_type: str):
        """Create a hotkey configuration row."""
        row = tk.Frame(parent, bg=self.THEME["bg"])
        row.pack(fill="x", pady=2, padx=5)
        
        tk.Label(row, text=label, font=("Courier", 10), fg=self.THEME["text"], bg=self.THEME["bg"], width=10, anchor="w").pack(side="left")
        
        btn = tk.Button(
            row,
            textvariable=var,
            font=("Courier", 9, "bold"),
            fg=self.THEME["text_bright"],
            bg=self.THEME["bg_dark"],
            activebackground=self.THEME["accent"],
            activeforeground=self.THEME["bg"],
            relief="flat",
            width=8,
            command=lambda: self._capture_hotkey(var, hotkey_type)
        )
        btn.pack(side="left")
    
    def _capture_hotkey(self, string_var, hotkey_type):
        """Capture next key press and set as hotkey."""
        if self._capturing_hotkey:
            return
            
        self._capturing_hotkey = True
        self.overlay_status_backup = self.status_var.get()
        self.status_var.set("Press any key...")
        
        def on_key(event):
            key = event.keysym
            # Cleanup key names
            if len(key) == 1:
                key = key.lower()
            
            string_var.set(key)
            self._capturing_hotkey = False
            self.root.unbind("<Key>")
            self.status_var.set(self.overlay_status_backup)
            
            # Call appropriate callback
            if hotkey_type == "heal" and self.on_heal_hotkey_change:
                self.on_heal_hotkey_change(key)
            elif hotkey_type == "critical" and self.on_critical_hotkey_change:
                self.on_critical_hotkey_change(key)
            elif hotkey_type == "mana" and self.on_mana_hotkey_change:
                self.on_mana_hotkey_change(key)
            elif hotkey_type == "eater" and self.on_eater_hotkey_change:
                self.on_eater_hotkey_change(key)
            elif hotkey_type == "haste" and self.on_haste_hotkey_change:
                self.on_haste_hotkey_change(key)
            elif hotkey_type == "skinner" and self.on_skinner_hotkey_change:
                self.on_skinner_hotkey_change(key)
            
            print(f"🔑 {hotkey_type} hotkey set to: {key}")
        
        # Bind key press
        self.root.bind("<Key>", on_key)
        self.root.focus_force() # Added this line as it was in the original _capture_hotkey
    
    def _add_separator(self, parent):
        """Add a thin separator line."""
        sep = tk.Frame(parent, height=1, bg=self.THEME["border_dark"])
        sep.pack(fill="x", pady=8)
    
    # Event handlers
    # ... (other handlers)
    
    def _on_skinner_toggle(self):
        if self.on_skinner_toggle:
            self.on_skinner_toggle(self.skinner_enabled.get())
    
    def _add_separator(self, parent):
        """Add a thin separator line."""
        sep = tk.Frame(parent, height=1, bg=self.THEME["border_dark"])
        sep.pack(fill="x", pady=8)
    
    # Event handlers
    def _toggle_bot(self):
        """Toggle bot start/stop."""
        if self.bot_active:
            self.bot_active = False
            self.start_btn.configure(text="▶️ Start")
            self.error_var.set("")
            self.error_label.pack_forget()
            
            # Enable inputs
            for entry in self.entries:
                entry.configure(state="normal")
            
            if self.on_stop:
                self.on_stop()
        else:
            # Check if configured
            if not self.hp_region_configured or not self.mana_region_configured:
                self.error_var.set("⚠️ Configure HP/Mana regions first!")
                self.error_label.pack(pady=3)
                return
            
            self.bot_active = True
            self.start_btn.configure(text="⏹️ Stop")
            self.error_var.set("")
            self.error_label.pack_forget()
            
            # Disable inputs
            for entry in self.entries:
                entry.configure(state="disabled")
            
            if self.on_start:
                self.on_start()
    
    def _select_hp_region(self):
        """Open region selector for HP."""
        self.root.withdraw()  # Hide main window
        
        def on_selected(region: Optional[Region]):
            self.root.deiconify()  # Show main window
            if region:
                self.hp_region_configured = True
                # Test OCR and show result
                result = self._test_region_ocr(region.as_tuple())
                if result:
                    self.hp_region_status.set(f"✓ Detected: {result[0]}/{result[1]}")
                else:
                    self.hp_region_status.set(f"✓ Region set (x:{region.x}, y:{region.y})")
                if self.on_hp_region_select:
                    self.on_hp_region_select(region.as_tuple())
        
        self.region_selector.select_region(self.root, on_selected, "Select HP Region")
    
    def _select_mana_region(self):
        """Open region selector for Mana."""
        self.root.withdraw()  # Hide main window
        
        def on_selected(region: Optional[Region]):
            self.root.deiconify()  # Show main window
            if region:
                self.mana_region_configured = True
                # Test OCR and show result
                result = self._test_region_ocr(region.as_tuple())
                if result:
                    self.mana_region_status.set(f"✓ Detected: {result[0]}/{result[1]}")
                else:
                    self.mana_region_status.set(f"✓ Region set (x:{region.x}, y:{region.y})")
                if self.on_mana_region_select:
                    self.on_mana_region_select(region.as_tuple())
        
        self.region_selector.select_region(self.root, on_selected, "Select Mana Region")
    
    def _test_region_ocr(self, region: tuple) -> Optional[tuple]:
        """Test OCR on a region and return (current, max) or None."""
        try:
            import mss
            import cv2
            import numpy as np
            from PIL import Image
            import pytesseract
            import re
            
            x, y, w, h = region
            
            with mss.mss() as sct:
                monitor = {"left": x, "top": y, "width": w, "height": h}
                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            
            arr = np.array(img.convert('L'))
            
            for thresh in [80, 100, 120, 140]:
                _, binary = cv2.threshold(arr, thresh, 255, cv2.THRESH_BINARY)
                scaled = cv2.resize(binary, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
                padded = cv2.copyMakeBorder(scaled, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=255)
                
                text = pytesseract.image_to_string(
                    padded,
                    config='--psm 7 -c tessedit_char_whitelist=0123456789/'
                ).strip()
                
                match = re.match(r'(\d+)[/|](\d+)', text.replace(" ", ""))
                if match:
                    return (int(match.group(1)), int(match.group(2)))
            
            return None
        except Exception as e:
            print(f"OCR test error: {e}")
            return None
    
    def _reset_config(self):
        """Reset all region configuration."""
        self.hp_region_configured = False
        self.mana_region_configured = False
        self.hp_region_status.set("✗ Not configured")
        self.mana_region_status.set("✗ Not configured")
        
        if self.on_reset_config:
            self.on_reset_config()
    
    def _on_heal_toggle(self):
        if self.on_heal_toggle:
            self.on_heal_toggle(self.heal_enabled.get())
    
    def _on_critical_toggle(self):
        if self.on_critical_toggle:
            self.on_critical_toggle(self.critical_enabled.get())
    
    def _on_mana_toggle(self):
        if self.on_mana_toggle:
            self.on_mana_toggle(self.mana_enabled.get())
            
    def _on_eater_toggle(self):
        if self.on_eater_toggle:
            self.on_eater_toggle(self.eater_enabled.get())
            
    def _on_haste_toggle(self):
        if self.on_haste_toggle:
            self.on_haste_toggle(self.haste_enabled.get())
            
    def _on_food_type_change(self, value):
        if self.on_food_type_change:
            self.on_food_type_change(value)
    
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
    
    def _on_mana_threshold_change(self, event=None):
        try:
            val = int(self.mana_threshold_var.get())
            if self.on_mana_threshold_change:
                self.on_mana_threshold_change(val)
        except ValueError:
            pass
    
    # Public API
    def set_status(self, status: str):
        if self.status_var:
            self.status_var.set(status)
    
    def set_hp(self, current: Optional[int], max_hp: Optional[int] = None):
        if self.hp_var:
            if current is not None and max_hp:
                pct = (current / max_hp) * 100
                self.hp_var.set(f"{current:,}/{max_hp:,} ({pct:.0f}%)")
            elif current is not None:
                self.hp_var.set(f"{current:,}")
            else:
                self.hp_var.set("---")
    
    def set_mana(self, current: Optional[int], max_mana: Optional[int] = None):
        if self.mana_var:
            if current is not None and max_mana:
                pct = (current / max_mana) * 100
                self.mana_var.set(f"{current:,}/{max_mana:,} ({pct:.0f}%)")
            elif current is not None:
                self.mana_var.set(f"{current:,}")
            else:
                self.mana_var.set("---")
    
    def set_hp_region_status(self, configured: bool, coords: Optional[tuple] = None):
        """Update HP region configuration status."""
        self.hp_region_configured = configured
        if self.hp_region_status:
            if configured and coords:
                x, y, w, h = coords
                self.hp_region_status.set(f"✓ {x}, {y} ({w}x{h})")
            else:
                self.hp_region_status.set("✗ Not configured")
    
    def set_mana_region_status(self, configured: bool, coords: Optional[tuple] = None):
        """Update Mana region configuration status."""
        self.mana_region_configured = configured
        if self.mana_region_status:
            if configured and coords:
                x, y, w, h = coords
                self.mana_region_status.set(f"✓ {x}, {y} ({w}x{h})")
            else:
                self.mana_region_status.set("✗ Not configured")
    
    def set_hotkeys(self, heal_key: str, critical_key: str, mana_key: str):
        """Set initial hotkey display values."""
        if self.heal_hotkey_var:
            self.heal_hotkey_var.set(heal_key)
        if self.critical_hotkey_var:
            self.critical_hotkey_var.set(critical_key)
        if self.mana_hotkey_var:
            self.mana_hotkey_var.set(mana_key)
    
    def show_error(self, message: str):
        """Show error message on Status tab."""
        if self.error_var:
            self.error_var.set(message)
        if self.error_label:
            self.error_label.pack(pady=3)
    
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


# Backward compatibility alias
BotOverlay = TibiaStyleOverlay


if __name__ == "__main__":
    overlay = TibiaStyleOverlay()
    overlay.run()
