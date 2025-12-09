"""
Windify Helper - Pixel Art Overlay UI
True pixel art styled overlay with beveled panels and retro aesthetics.
"""

import tkinter as tk
from tkinter import font as tkfont
from typing import Callable, Optional
from region_selector import RegionSelector, Region


class PixelArtPanel(tk.Canvas):
    """A canvas-based panel with pixel art beveled borders."""
    
    def __init__(self, parent, bg_color="#1a1a2e", border_size=4, **kwargs):
        # Remove width/height from kwargs if present, we'll handle them
        width = kwargs.pop('width', 250)
        height = kwargs.pop('height', 100)
        
        super().__init__(
            parent, 
            width=width, 
            height=height,
            bg=bg_color,
            highlightthickness=0,
            **kwargs
        )
        
        self.bg_color = bg_color
        self.border_size = border_size
        
        # Pixel art border colors (classic RPG style)
        self.colors = {
            'highlight': '#4a4a6a',      # Top-left highlight
            'highlight_inner': '#3a3a5a', # Inner highlight
            'shadow': '#0a0a15',          # Bottom-right shadow
            'shadow_inner': '#15152a',    # Inner shadow
            'corner': '#2a2a4a',          # Corner pixels
        }
        
        self._draw_pixel_border()
        
        # Inner frame for content
        self.inner_frame = tk.Frame(self, bg=bg_color)
        self.create_window(
            border_size + 2, 
            border_size + 2, 
            window=self.inner_frame, 
            anchor='nw',
            width=width - (border_size + 2) * 2,
            height=height - (border_size + 2) * 2
        )
    
    def _draw_pixel_border(self):
        """Draw pixel art beveled border."""
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        bs = self.border_size
        
        # Outer highlight (top and left) - creates 3D raised effect
        for i in range(bs):
            shade = self.colors['highlight'] if i < bs//2 else self.colors['highlight_inner']
            # Top edge
            self.create_line(i, i, w-i, i, fill=shade, width=1)
            # Left edge  
            self.create_line(i, i, i, h-i, fill=shade, width=1)
        
        # Outer shadow (bottom and right)
        for i in range(bs):
            shade = self.colors['shadow'] if i < bs//2 else self.colors['shadow_inner']
            # Bottom edge
            self.create_line(i, h-1-i, w-i, h-1-i, fill=shade, width=1)
            # Right edge
            self.create_line(w-1-i, i, w-1-i, h-i, fill=shade, width=1)
        
        # Corner pixels for authentic look
        for i in range(bs):
            # Top-right corner transition
            self.create_rectangle(w-1-i, i, w-i, i+1, fill=self.colors['corner'], outline='')
            # Bottom-left corner transition  
            self.create_rectangle(i, h-1-i, i+1, h-i, fill=self.colors['corner'], outline='')
    
    def get_frame(self):
        """Return the inner frame for adding widgets."""
        return self.inner_frame


class PixelButton(tk.Canvas):
    """A pixel art styled button."""
    
    def __init__(self, parent, text="", command=None, width=100, height=28, 
                 bg_color="#2a2a4a", fg_color="#00f0ff", **kwargs):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent.cget('bg') if hasattr(parent, 'cget') else '#1a1a2e',
            highlightthickness=0,
            **kwargs
        )
        
        self.text = text
        self.command = command
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.pressed = False
        
        self._draw_button()
        
        # Bindings
        self.bind('<Button-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
    
    def _draw_button(self, pressed=False):
        """Draw the pixel art button."""
        self.delete('all')
        
        w, h = self.width, self.height
        bs = 3  # Border size
        
        if pressed:
            # Pressed state - inverted bevel
            highlight = '#0a0a15'
            shadow = '#4a4a6a'
            bg = '#1a1a2e'
        else:
            # Normal state
            highlight = '#4a4a6a'
            shadow = '#0a0a15'
            bg = self.bg_color
        
        # Background
        self.create_rectangle(bs, bs, w-bs, h-bs, fill=bg, outline='')
        
        # Top and left highlight
        for i in range(bs):
            self.create_line(i, i, w-i, i, fill=highlight, width=1)
            self.create_line(i, i, i, h-i, fill=highlight, width=1)
        
        # Bottom and right shadow
        for i in range(bs):
            self.create_line(i, h-1-i, w-i, h-1-i, fill=shadow, width=1)
            self.create_line(w-1-i, i, w-1-i, h-i, fill=shadow, width=1)
        
        # Text
        text_y = h // 2 + (2 if pressed else 0)
        self.create_text(
            w // 2, 
            text_y,
            text=self.text,
            fill=self.fg_color,
            font=('Consolas', 10, 'bold')
        )
    
    def _on_press(self, event):
        self.pressed = True
        self._draw_button(pressed=True)
    
    def _on_release(self, event):
        self.pressed = False
        self._draw_button(pressed=False)
        if self.command:
            self.command()
    
    def _on_enter(self, event):
        self.fg_color = '#80ffff'
        self._draw_button()
    
    def _on_leave(self, event):
        self.fg_color = '#00f0ff'
        self._draw_button()
    
    def configure_text(self, text):
        self.text = text
        self._draw_button()


class TibiaStyleOverlay:
    """True pixel art styled overlay with authentic retro aesthetics."""
    
    # Pixel Art Theme
    THEME = {
        # Base colors
        "bg": "#0d0d1a",
        "bg_dark": "#08080f",
        "bg_light": "#1a1a2e",
        "bg_panel": "#151525",
        
        # Pixel art borders
        "border_highlight": "#4a4a6a",
        "border_shadow": "#0a0a15",
        "border_mid": "#2a2a4a",
        
        # Text colors
        "text": "#a0a0c0",
        "text_dim": "#606080",
        "text_bright": "#ffffff",
        
        # Status colors
        "hp": "#ff4466",
        "hp_dark": "#aa2244",
        "mana": "#00ccff",
        "mana_dark": "#0088aa",
        
        # Neon accents
        "accent": "#00f0ff",
        "accent_bright": "#80ffff",
        "accent_alt": "#ff00aa",
        "gold": "#ffd700",
        "success": "#00ff88",
        "error": "#ff3355",
        "warning": "#ffaa00",
        
        # Feature colors
        "eater": "#ffaa00",
        "haste": "#00ff88",
        "skinner": "#ff6600",
    }

    # Icons
    ICONS = {
        "hp": "♥",
        "mana": "◆",
        "heal": "✚",
        "critical": "⚡",
        "eater": "※",
        "haste": "»",
        "skinner": "†",
        "start": "▶",
        "stop": "■",
        "config": "⚙",
        "status": "◈",
        "check": "✓",
        "cross": "✗",
    }
    
    def __init__(self):
        self.root: Optional[tk.Tk] = None
        self.running = False
        self.bot_active = False
        
        # Callbacks (all preserved from original)
        self.on_start: Optional[Callable] = None
        self.on_stop: Optional[Callable] = None
        self.on_hp_region_select: Optional[Callable] = None
        self.on_mana_region_select: Optional[Callable] = None
        self.on_reset_config: Optional[Callable] = None
        self.on_heal_toggle: Optional[Callable[[bool], None]] = None
        self.on_critical_toggle: Optional[Callable[[bool], None]] = None
        self.on_mana_toggle: Optional[Callable[[bool], None]] = None
        self.on_heal_threshold_change: Optional[Callable[[int], None]] = None
        self.on_critical_threshold_change: Optional[Callable[[int], None]] = None
        self.on_mana_threshold_change: Optional[Callable[[int], None]] = None
        self.on_heal_hotkey_change: Optional[Callable[[str], None]] = None
        self.on_critical_hotkey_change: Optional[Callable[[str], None]] = None
        self.on_mana_hotkey_change: Optional[Callable[[str], None]] = None
        self.on_eater_toggle: Optional[Callable[[bool], None]] = None
        self.on_food_type_change: Optional[Callable[[str], None]] = None
        self.on_eater_hotkey_change: Optional[Callable[[str], None]] = None
        self.on_haste_toggle: Optional[Callable[[bool], None]] = None
        self.on_haste_hotkey_change: Optional[Callable[[str], None]] = None
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
        
        # Control vars
        self.heal_enabled = None
        self.critical_enabled = None
        self.mana_enabled = None
        self.heal_threshold_var = None
        self.critical_threshold_var = None
        self.mana_threshold_var = None
        self.eater_enabled = None
        self.food_type_var = None
        self.eater_hotkey_var = None
        self.haste_enabled = None
        self.haste_hotkey_var = None
        self.skinner_enabled = None
        self.skinner_hotkey_var = None
        
        # Region selector
        self.region_selector = RegionSelector()
        self.monitor_geometry = None  # Will be set by main.py
        
        # Config state
        self.hp_region_configured = False
        self.mana_region_configured = False
        
        # UI references
        self.start_btn: Optional[PixelButton] = None
        self.entries = []
        self.error_var = None
        self.error_label = None
        self.heal_hotkey_var = None
        self.critical_hotkey_var = None
        self.mana_hotkey_var = None
        self._capturing_hotkey = False
        self._capture_callback = None
    
    def create_window(self):
        """Create the pixel art overlay window."""
        self.root = tk.Tk()
        self.root.title("Pixel Bot")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.configure(bg=self.THEME["bg"])
        self.root.geometry("290x580+20+100")
        
        # Initialize hotkey vars
        self.eater_hotkey_var = tk.StringVar(value="]")
        self.haste_hotkey_var = tk.StringVar(value="x")
        self.skinner_hotkey_var = tk.StringVar(value="[")
        self.heal_hotkey_var = tk.StringVar(value="F1")
        self.critical_hotkey_var = tk.StringVar(value="F2")
        self.mana_hotkey_var = tk.StringVar(value="F4")
        
        # Main container with pixel art border
        self.main_panel = PixelArtPanel(
            self.root,
            bg_color=self.THEME["bg"],
            border_size=6,
            width=286,
            height=576
        )
        self.main_panel.pack(padx=2, pady=2)
        
        main_frame = self.main_panel.get_frame()
        
        # Header
        self._create_header(main_frame)
        
        # Tabs
        self._create_tabs(main_frame)
        
        # Content
        self.content_frame = tk.Frame(main_frame, bg=self.THEME["bg"])
        self.content_frame.pack(fill="both", expand=True, padx=4, pady=4)
        
        # Create tab content
        self._create_status_tab()
        self._create_config_tab()
        self._show_tab("status")
        
        self.running = True
    
    def _create_header(self, parent):
        """Create pixel art header."""
        header = tk.Frame(parent, bg=self.THEME["bg_dark"], height=32)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        # Pixel decoration
        deco_frame = tk.Frame(header, bg=self.THEME["bg_dark"])
        deco_frame.pack(side="left", fill="y")
        
        # Pixel diamond icon
        tk.Label(
            deco_frame,
            text="◆◇◆",
            font=("Consolas", 8),
            fg=self.THEME["accent"],
            bg=self.THEME["bg_dark"]
        ).pack(side="left", padx=6)
        
        # Title
        tk.Label(
            header,
            text="PIXEL BOT",
            font=("Consolas", 11, "bold"),
            fg=self.THEME["gold"],
            bg=self.THEME["bg_dark"]
        ).pack(side="left", padx=4)
        
        # Version
        tk.Label(
            header,
            text="v2",
            font=("Consolas", 8),
            fg=self.THEME["text_dim"],
            bg=self.THEME["bg_dark"]
        ).pack(side="left")
        
        # Close button
        close_btn = tk.Label(
            header,
            text="[X]",
            font=("Consolas", 9, "bold"),
            fg=self.THEME["text_dim"],
            bg=self.THEME["bg_dark"],
            cursor="hand2"
        )
        close_btn.pack(side="right", padx=4)
        close_btn.bind("<Button-1>", lambda e: self.root.destroy())
        close_btn.bind("<Enter>", lambda e: close_btn.config(fg=self.THEME["error"]))
        close_btn.bind("<Leave>", lambda e: close_btn.config(fg=self.THEME["text_dim"]))
        
        # Drag bindings
        def start_move(event):
            self.root.x = event.x
            self.root.y = event.y

        def do_move(event):
            x = self.root.winfo_x() + event.x - self.root.x
            y = self.root.winfo_y() + event.y - self.root.y
            self.root.geometry(f"+{x}+{y}")

        for w in [header, deco_frame]:
            w.bind("<ButtonPress-1>", start_move)
            w.bind("<B1-Motion>", do_move)
    
    def _create_tabs(self, parent):
        """Create pixel art style tabs."""
        tabs_frame = tk.Frame(parent, bg=self.THEME["bg"])
        tabs_frame.pack(fill="x", pady=4)
        
        # Pixel line top
        tk.Frame(tabs_frame, height=2, bg=self.THEME["border_highlight"]).pack(fill="x")
        
        btns_frame = tk.Frame(tabs_frame, bg=self.THEME["bg_panel"])
        btns_frame.pack(fill="x")
        
        # Status tab
        self.tab_buttons["status"] = tk.Label(
            btns_frame,
            text=f"[{self.ICONS['status']} STATUS]",
            font=("Consolas", 9, "bold"),
            fg=self.THEME["accent"],
            bg=self.THEME["bg_light"],
            padx=8,
            pady=4,
            cursor="hand2"
        )
        self.tab_buttons["status"].pack(side="left", padx=2, pady=2)
        self.tab_buttons["status"].bind("<Button-1>", lambda e: self._show_tab("status"))
        
        # Config tab
        self.tab_buttons["config"] = tk.Label(
            btns_frame,
            text=f"[{self.ICONS['config']} CONFIG]",
            font=("Consolas", 9, "bold"),
            fg=self.THEME["text_dim"],
            bg=self.THEME["bg_panel"],
            padx=8,
            pady=4,
            cursor="hand2"
        )
        self.tab_buttons["config"].pack(side="left", padx=2, pady=2)
        self.tab_buttons["config"].bind("<Button-1>", lambda e: self._show_tab("config"))
        
        # Pixel line bottom
        tk.Frame(tabs_frame, height=2, bg=self.THEME["border_shadow"]).pack(fill="x")
    
    def _show_tab(self, tab_id: str):
        """Switch tabs with pixel art styling."""
        self.current_tab = tab_id
        
        for name, btn in self.tab_buttons.items():
            if name == tab_id:
                btn.configure(fg=self.THEME["accent"], bg=self.THEME["bg_light"])
            else:
                btn.configure(fg=self.THEME["text_dim"], bg=self.THEME["bg_panel"])
        
        for tid, frame in self.tab_frames.items():
            if tid == tab_id:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()
    
    def _create_pixel_section(self, parent, title, icon=""):
        """Create a pixel art section header."""
        section = tk.Frame(parent, bg=self.THEME["bg"])
        section.pack(fill="x", pady=(8, 4))
        
        # Left pixels
        tk.Label(
            section,
            text="══",
            font=("Consolas", 8),
            fg=self.THEME["border_highlight"],
            bg=self.THEME["bg"]
        ).pack(side="left")
        
        # Title with icon
        title_text = f" {icon} {title} " if icon else f" {title} "
        tk.Label(
            section,
            text=title_text,
            font=("Consolas", 9, "bold"),
            fg=self.THEME["gold"],
            bg=self.THEME["bg"]
        ).pack(side="left")
        
        # Right pixels (fill)
        tk.Label(
            section,
            text="═" * 20,
            font=("Consolas", 8),
            fg=self.THEME["border_highlight"],
            bg=self.THEME["bg"]
        ).pack(side="left", fill="x", expand=True)
        
        return section
    
    def _create_status_tab(self):
        """Create status tab with pixel art panels."""
        frame = tk.Frame(self.content_frame, bg=self.THEME["bg"])
        self.tab_frames["status"] = frame
        
        # Status panel
        status_panel = PixelArtPanel(frame, bg_color=self.THEME["bg_panel"], 
                                      border_size=3, width=258, height=36)
        status_panel.pack(fill="x", pady=4)
        status_inner = status_panel.get_frame()
        
        status_row = tk.Frame(status_inner, bg=self.THEME["bg_panel"])
        status_row.pack(fill="x", pady=2)
        
        tk.Label(
            status_row,
            text="●",
            font=("Consolas", 10),
            fg=self.THEME["success"],
            bg=self.THEME["bg_panel"]
        ).pack(side="left", padx=4)
        
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(
            status_row,
            textvariable=self.status_var,
            font=("Consolas", 10),
            fg=self.THEME["text"],
            bg=self.THEME["bg_panel"]
        ).pack(side="left")
        
        # Vitals section
        self._create_pixel_section(frame, "VITALS", self.ICONS["hp"])
        
        vitals_panel = PixelArtPanel(frame, bg_color=self.THEME["bg_panel"],
                                      border_size=3, width=258, height=60)
        vitals_panel.pack(fill="x")
        vitals_inner = vitals_panel.get_frame()
        
        # HP
        hp_row = tk.Frame(vitals_inner, bg=self.THEME["bg_panel"])
        hp_row.pack(fill="x", pady=2)
        tk.Label(hp_row, text=f"{self.ICONS['hp']} HP:", font=("Consolas", 10, "bold"),
                fg=self.THEME["hp"], bg=self.THEME["bg_panel"], width=8, anchor="w").pack(side="left")
        self.hp_var = tk.StringVar(value="---/---")
        tk.Label(hp_row, textvariable=self.hp_var, font=("Consolas", 10),
                fg=self.THEME["text_bright"], bg=self.THEME["bg_panel"]).pack(side="right", padx=4)
        
        # Mana
        mana_row = tk.Frame(vitals_inner, bg=self.THEME["bg_panel"])
        mana_row.pack(fill="x", pady=2)
        tk.Label(mana_row, text=f"{self.ICONS['mana']} MP:", font=("Consolas", 10, "bold"),
                fg=self.THEME["mana"], bg=self.THEME["bg_panel"], width=8, anchor="w").pack(side="left")
        self.mana_var = tk.StringVar(value="---/---")
        tk.Label(mana_row, textvariable=self.mana_var, font=("Consolas", 10),
                fg=self.THEME["text_bright"], bg=self.THEME["bg_panel"]).pack(side="right", padx=4)
        
        # Controls section
        self._create_pixel_section(frame, "CONTROLS", "⚔")
        
        controls_panel = PixelArtPanel(frame, bg_color=self.THEME["bg_panel"],
                                        border_size=3, width=258, height=100)
        controls_panel.pack(fill="x")
        controls_inner = controls_panel.get_frame()
        
        # Heal controls
        self.heal_enabled = tk.BooleanVar(value=True)
        self.heal_threshold_var = tk.StringVar(value="75")
        self._create_heal_row(controls_inner, f"{self.ICONS['heal']} Heal", self.heal_enabled,
                             self.heal_threshold_var, self._on_heal_toggle,
                             self._on_heal_threshold_change, self.THEME["hp"])
        
        self.critical_enabled = tk.BooleanVar(value=True)
        self.critical_threshold_var = tk.StringVar(value="50")
        self._create_heal_row(controls_inner, f"{self.ICONS['critical']} Crit", self.critical_enabled,
                             self.critical_threshold_var, self._on_critical_toggle,
                             self._on_critical_threshold_change, self.THEME["error"])
        
        self.mana_enabled = tk.BooleanVar(value=True)
        self.mana_threshold_var = tk.StringVar(value="60")
        self._create_heal_row(controls_inner, f"{self.ICONS['mana']} Mana", self.mana_enabled,
                             self.mana_threshold_var, self._on_mana_toggle,
                             self._on_mana_threshold_change, self.THEME["mana"])
        
        # Extras section
        self._create_pixel_section(frame, "EXTRAS", "★")
        
        extras_panel = PixelArtPanel(frame, bg_color=self.THEME["bg_panel"],
                                      border_size=3, width=258, height=80)
        extras_panel.pack(fill="x")
        extras_inner = extras_panel.get_frame()
        
        self.eater_enabled = tk.BooleanVar(value=False)
        self._create_simple_toggle(extras_inner, f"{self.ICONS['eater']} Eater", 
                                   self.eater_enabled, self._on_eater_toggle,
                                   self.THEME["eater"], self.eater_hotkey_var)
        
        self.haste_enabled = tk.BooleanVar(value=False)
        self._create_simple_toggle(extras_inner, f"{self.ICONS['haste']} Haste",
                                   self.haste_enabled, self._on_haste_toggle,
                                   self.THEME["haste"], self.haste_hotkey_var)
        
        self.skinner_enabled = tk.BooleanVar(value=False)
        self._create_simple_toggle(extras_inner, f"{self.ICONS['skinner']} Skin",
                                   self.skinner_enabled, self._on_skinner_toggle,
                                   self.THEME["skinner"], self.skinner_hotkey_var)
        
        # Start button
        btn_frame = tk.Frame(frame, bg=self.THEME["bg"])
        btn_frame.pack(fill="x", pady=10)
        
        self.start_btn = PixelButton(
            btn_frame,
            text=f"{self.ICONS['start']} START",
            command=self._toggle_bot,
            width=140,
            height=32,
            bg_color="#1a4a2a",
            fg_color=self.THEME["success"]
        )
        self.start_btn.pack()
        
        # Error label
        self.error_var = tk.StringVar(value="")
        self.error_label = tk.Label(
            frame,
            textvariable=self.error_var,
            font=("Consolas", 9),
            fg=self.THEME["error"],
            bg=self.THEME["bg"]
        )
    
    def _create_simple_toggle(self, parent, label, var, cmd, color, hotkey_var=None):
        """Create pixel art toggle row."""
        row = tk.Frame(parent, bg=self.THEME["bg_panel"])
        row.pack(fill="x", pady=1)
        
        cb = tk.Checkbutton(
            row, text=label, variable=var, command=cmd,
            font=("Consolas", 9), fg=color, bg=self.THEME["bg_panel"],
            selectcolor=self.THEME["bg_dark"], activebackground=self.THEME["bg_panel"],
            highlightthickness=0
        )
        cb.pack(side="left")
        
        if hotkey_var:
            lbl = tk.Label(row, text=f"[{hotkey_var.get()}]", font=("Consolas", 8),
                          fg=self.THEME["text_dim"], bg=self.THEME["bg_panel"])
            lbl.pack(side="right", padx=4)
            hotkey_var.trace_add("write", lambda *a: lbl.config(text=f"[{hotkey_var.get()}]"))
    
    def _create_heal_row(self, parent, label, var, thresh_var, toggle_cmd, thresh_cmd, color):
        """Create heal control row."""
        row = tk.Frame(parent, bg=self.THEME["bg_panel"])
        row.pack(fill="x", pady=1)
        
        cb = tk.Checkbutton(
            row, text=label, variable=var, command=toggle_cmd,
            font=("Consolas", 9), fg=color, bg=self.THEME["bg_panel"],
            selectcolor=self.THEME["bg_dark"], activebackground=self.THEME["bg_panel"],
            highlightthickness=0
        )
        cb.pack(side="left")
        
        # Threshold
        tk.Label(row, text="@", font=("Consolas", 8), fg=self.THEME["text_dim"],
                bg=self.THEME["bg_panel"]).pack(side="right")
        tk.Label(row, text="%", font=("Consolas", 8), fg=self.THEME["text_dim"],
                bg=self.THEME["bg_panel"]).pack(side="right")
        
        entry = tk.Entry(row, textvariable=thresh_var, width=3, font=("Consolas", 9),
                        fg=self.THEME["text_bright"], bg=self.THEME["bg_dark"],
                        insertbackground=self.THEME["accent"], relief="flat", justify="center")
        entry.pack(side="right")
        entry.bind("<Return>", thresh_cmd)
        entry.bind("<FocusOut>", thresh_cmd)
        self.entries.append(entry)
    
    def _create_config_tab(self):
        """Create config tab with pixel art panels."""
        frame = tk.Frame(self.content_frame, bg=self.THEME["bg"])
        self.tab_frames["config"] = frame
        
        # Regions section
        self._create_pixel_section(frame, "REGIONS", "◎")
        
        region_panel = PixelArtPanel(frame, bg_color=self.THEME["bg_panel"],
                                      border_size=3, width=258, height=90)
        region_panel.pack(fill="x")
        region_inner = region_panel.get_frame()
        
        # HP Region
        hp_row = tk.Frame(region_inner, bg=self.THEME["bg_panel"])
        hp_row.pack(fill="x", pady=2)
        tk.Label(hp_row, text=f"{self.ICONS['hp']} HP Region", font=("Consolas", 9),
                fg=self.THEME["hp"], bg=self.THEME["bg_panel"]).pack(side="left")
        
        hp_btn = PixelButton(hp_row, text="SELECT", command=self._select_hp_region,
                            width=70, height=20, bg_color=self.THEME["bg_light"])
        hp_btn.pack(side="right", padx=2)
        
        self.hp_region_status = tk.StringVar(value=f"{self.ICONS['cross']} Not set")
        tk.Label(region_inner, textvariable=self.hp_region_status, font=("Consolas", 8),
                fg=self.THEME["text_dim"], bg=self.THEME["bg_panel"]).pack(anchor="w")
        
        # Mana Region
        mana_row = tk.Frame(region_inner, bg=self.THEME["bg_panel"])
        mana_row.pack(fill="x", pady=2)
        tk.Label(mana_row, text=f"{self.ICONS['mana']} Mana Region", font=("Consolas", 9),
                fg=self.THEME["mana"], bg=self.THEME["bg_panel"]).pack(side="left")
        
        mana_btn = PixelButton(mana_row, text="SELECT", command=self._select_mana_region,
                              width=70, height=20, bg_color=self.THEME["bg_light"])
        mana_btn.pack(side="right", padx=2)
        
        self.mana_region_status = tk.StringVar(value=f"{self.ICONS['cross']} Not set")
        tk.Label(region_inner, textvariable=self.mana_region_status, font=("Consolas", 8),
                fg=self.THEME["text_dim"], bg=self.THEME["bg_panel"]).pack(anchor="w")
        
        # Food section
        self._create_pixel_section(frame, "FOOD", self.ICONS["eater"])
        
        food_panel = PixelArtPanel(frame, bg_color=self.THEME["bg_panel"],
                                    border_size=3, width=258, height=55)
        food_panel.pack(fill="x")
        food_inner = food_panel.get_frame()
        
        food_row = tk.Frame(food_inner, bg=self.THEME["bg_panel"])
        food_row.pack(fill="x", pady=2)
        tk.Label(food_row, text="Type:", font=("Consolas", 9),
                fg=self.THEME["text"], bg=self.THEME["bg_panel"]).pack(side="left")
        
        self.food_type_var = tk.StringVar(value="fire_mushroom")
        om = tk.OptionMenu(food_row, self.food_type_var, "fire_mushroom", "brown_mushroom",
                          command=self._on_food_type_change)
        om.configure(bg=self.THEME["bg_dark"], fg=self.THEME["text"], highlightthickness=0,
                    relief="flat", font=("Consolas", 8))
        om["menu"].config(bg=self.THEME["bg_dark"], fg=self.THEME["text"])
        om.pack(side="right")
        
        self._create_hotkey_row(food_inner, "Key:", self.eater_hotkey_var, "eater")
        
        # Hotkeys section
        self._create_pixel_section(frame, "HOTKEYS", "♪")
        
        hotkey_panel = PixelArtPanel(frame, bg_color=self.THEME["bg_panel"],
                                      border_size=3, width=258, height=130)
        hotkey_panel.pack(fill="x")
        hotkey_inner = hotkey_panel.get_frame()
        
        self._create_hotkey_row(hotkey_inner, f"{self.ICONS['heal']} Heal:", self.heal_hotkey_var, "heal")
        self._create_hotkey_row(hotkey_inner, f"{self.ICONS['critical']} Crit:", self.critical_hotkey_var, "critical")
        self._create_hotkey_row(hotkey_inner, f"{self.ICONS['mana']} Mana:", self.mana_hotkey_var, "mana")
        self._create_hotkey_row(hotkey_inner, f"{self.ICONS['haste']} Haste:", self.haste_hotkey_var, "haste")
        self._create_hotkey_row(hotkey_inner, f"{self.ICONS['skinner']} Skin:", self.skinner_hotkey_var, "skinner")
        
        # Reset button
        btn_frame = tk.Frame(frame, bg=self.THEME["bg"])
        btn_frame.pack(fill="x", pady=10)
        
        reset_btn = PixelButton(
            btn_frame,
            text="RESET ALL",
            command=self._reset_config,
            width=100,
            height=26,
            bg_color="#4a1a1a",
            fg_color=self.THEME["error"]
        )
        reset_btn.pack()
    
    def _create_hotkey_row(self, parent, label, var, hk_type):
        """Create hotkey config row."""
        row = tk.Frame(parent, bg=self.THEME["bg_panel"])
        row.pack(fill="x", pady=1)
        
        tk.Label(row, text=label, font=("Consolas", 9), fg=self.THEME["text"],
                bg=self.THEME["bg_panel"], width=10, anchor="w").pack(side="left")
        
        btn = tk.Label(
            row, textvariable=var, font=("Consolas", 9, "bold"),
            fg=self.THEME["accent"], bg=self.THEME["bg_dark"],
            width=6, cursor="hand2", relief="flat"
        )
        btn.pack(side="right", padx=2)
        btn.bind("<Button-1>", lambda e: self._capture_hotkey(var, hk_type))
    
    # ==================== CALLBACKS ====================
    
    def _capture_hotkey(self, var, hk_type):
        if self._capturing_hotkey:
            return
        self._capturing_hotkey = True
        backup = self.status_var.get()
        self.status_var.set("Press key...")
        
        def on_key(e):
            key = e.keysym.lower() if len(e.keysym) == 1 else e.keysym
            var.set(key)
            self._capturing_hotkey = False
            self.root.unbind("<Key>")
            self.status_var.set(backup)
            
            callbacks = {
                "heal": self.on_heal_hotkey_change,
                "critical": self.on_critical_hotkey_change,
                "mana": self.on_mana_hotkey_change,
                "eater": self.on_eater_hotkey_change,
                "haste": self.on_haste_hotkey_change,
                "skinner": self.on_skinner_hotkey_change,
            }
            if callbacks.get(hk_type):
                callbacks[hk_type](key)
        
        self.root.bind("<Key>", on_key)
        self.root.focus_force()
    
    def _toggle_bot(self):
        if self.bot_active:
            self.bot_active = False
            self.start_btn.text = f"{self.ICONS['start']} START"
            self.start_btn.bg_color = "#1a4a2a"
            self.start_btn.fg_color = self.THEME["success"]
            self.start_btn._draw_button()
            self.error_var.set("")
            self.error_label.pack_forget()
            for e in self.entries:
                e.config(state="normal")
            if self.on_stop:
                self.on_stop()
        else:
            if not self.hp_region_configured or not self.mana_region_configured:
                self.error_var.set("⚠ Configure regions first!")
                self.error_label.pack(pady=2)
                return
            self.bot_active = True
            self.start_btn.text = f"{self.ICONS['stop']} STOP"
            self.start_btn.bg_color = "#4a1a1a"
            self.start_btn.fg_color = self.THEME["error"]
            self.start_btn._draw_button()
            self.error_var.set("")
            self.error_label.pack_forget()
            for e in self.entries:
                e.config(state="disabled")
            if self.on_start:
                self.on_start()
    
    def _select_hp_region(self):
        """Open region selector for HP."""
        self.root.withdraw()
        # Pass monitor geometry for correct screen placement
        self.region_selector.select_region(
            self.root, 
            self._handle_hp_selection, 
            "Select HP Region",
            monitor_geometry=self.monitor_geometry
        )

    def _select_mana_region(self):
        """Open region selector for Mana."""
        self.root.withdraw()
        self.region_selector.select_region(
            self.root, 
            self._handle_mana_selection, 
            "Select Mana Region",
            monitor_geometry=self.monitor_geometry
        )
    
    def _test_region_ocr(self, region):
        try:
            import mss, cv2, numpy as np, re
            from PIL import Image
            import pytesseract
            x, y, w, h = region
            with mss.mss() as sct:
                img = Image.frombytes("RGB", (mon := sct.grab({"left": x, "top": y, "width": w, "height": h})).size,
                                      mon.bgra, "raw", "BGRX")
            arr = np.array(img.convert('L'))
            for t in [80, 100, 120, 140]:
                _, b = cv2.threshold(arr, t, 255, cv2.THRESH_BINARY)
                s = cv2.resize(b, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
                p = cv2.copyMakeBorder(s, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=255)
                txt = pytesseract.image_to_string(p, config='--psm 7 -c tessedit_char_whitelist=0123456789/').strip()
                m = re.match(r'(\d+)[/|](\d+)', txt.replace(" ", ""))
                if m:
                    return (int(m.group(1)), int(m.group(2)))
            return None
        except Exception as e:
            print(f"OCR error: {e}")
            return None
    
    def _reset_config(self):
        self.hp_region_configured = False
        self.mana_region_configured = False
        self.hp_region_status.set(f"{self.ICONS['cross']} Not set")
        self.mana_region_status.set(f"{self.ICONS['cross']} Not set")
        if self.on_reset_config:
            self.on_reset_config()
    
    def _on_heal_toggle(self):
        if self.on_heal_toggle: self.on_heal_toggle(self.heal_enabled.get())
    def _on_critical_toggle(self):
        if self.on_critical_toggle: self.on_critical_toggle(self.critical_enabled.get())
    def _on_mana_toggle(self):
        if self.on_mana_toggle: self.on_mana_toggle(self.mana_enabled.get())
    def _on_eater_toggle(self):
        if self.on_eater_toggle: self.on_eater_toggle(self.eater_enabled.get())
    def _on_haste_toggle(self):
        if self.on_haste_toggle: self.on_haste_toggle(self.haste_enabled.get())
    def _on_skinner_toggle(self):
        if self.on_skinner_toggle: self.on_skinner_toggle(self.skinner_enabled.get())
    def _on_food_type_change(self, val):
        if self.on_food_type_change: self.on_food_type_change(val)
    def _on_heal_threshold_change(self, e=None):
        try:
            if self.on_heal_threshold_change: self.on_heal_threshold_change(int(self.heal_threshold_var.get()))
        except: pass
    def _on_critical_threshold_change(self, e=None):
        try:
            if self.on_critical_threshold_change: self.on_critical_threshold_change(int(self.critical_threshold_var.get()))
        except: pass
    def _on_mana_threshold_change(self, e=None):
        try:
            if self.on_mana_threshold_change: self.on_mana_threshold_change(int(self.mana_threshold_var.get()))
        except: pass
    
    # ==================== PUBLIC API ====================
    
    def set_status(self, s):
        if self.status_var: self.status_var.set(s)
    
    def set_hp(self, c, m=None):
        if self.hp_var:
            if c is not None and m:
                self.hp_var.set(f"{c:,}/{m:,} ({100*c//m}%)")
            elif c is not None:
                self.hp_var.set(f"{c:,}")
            else:
                self.hp_var.set("---")
    
    def set_mana(self, c, m=None):
        if self.mana_var:
            if c is not None and m:
                self.mana_var.set(f"{c:,}/{m:,} ({100*c//m}%)")
            elif c is not None:
                self.mana_var.set(f"{c:,}")
            else:
                self.mana_var.set("---")
    
    def set_hp_region_status(self, cfg, coords=None):
        self.hp_region_configured = cfg
        if self.hp_region_status:
            if cfg and coords:
                self.hp_region_status.set(f"{self.ICONS['check']} {coords[0]},{coords[1]}")
            else:
                self.hp_region_status.set(f"{self.ICONS['cross']} Not set")
    
    def set_mana_region_status(self, cfg, coords=None):
        self.mana_region_configured = cfg
        if self.mana_region_status:
            if cfg and coords:
                self.mana_region_status.set(f"{self.ICONS['check']} {coords[0]},{coords[1]}")
            else:
                self.mana_region_status.set(f"{self.ICONS['cross']} Not set")
    
    def set_hotkeys(self, h, c, m):
        if self.heal_hotkey_var: self.heal_hotkey_var.set(h)
        if self.critical_hotkey_var: self.critical_hotkey_var.set(c)
        if self.mana_hotkey_var: self.mana_hotkey_var.set(m)
    
    def show_error(self, msg):
        if self.error_var: self.error_var.set(msg)
        if self.error_label: self.error_label.pack(pady=2)
    
    def update(self):
        if self.root: self.root.update()
    
    def run(self):
        self.create_window()
        self.root.mainloop()
    
    def close(self):
        self.running = False
        if self.root: self.root.destroy()


BotOverlay = TibiaStyleOverlay

if __name__ == "__main__":
    TibiaStyleOverlay().run()
