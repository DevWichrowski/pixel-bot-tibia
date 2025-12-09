"""
Windify Helper - Main with Overlay and Auto-Heal
Uses user-defined regions for HP/Mana reading.
"""

import time
import threading
import mss
from PIL import Image
from config import BOT_NAME, REFRESH_RATE
from hp_mana_reader import HPManaReader
from overlay import TibiaStyleOverlay
from healer import AutoHealer, press_key
from eater import AutoEater
from haste import AutoHaste
from skinner import AutoSkinner
from user_config import ConfigManager
import platform


class TibiaBot:
    def __init__(self, overlay: TibiaStyleOverlay, config_manager: ConfigManager):
        self.overlay = overlay
        self.config_manager = config_manager
        self.reader = HPManaReader()
        self.healer = AutoHealer(press_key)
        self.eater = AutoEater(press_key)
        self.haste = AutoHaste(press_key)
        self.skinner = AutoSkinner(press_key)
        self.running = False
        self.active = False
        self.sct = mss.mss()  # Screen capture
        
        # Load saved regions
        self._load_saved_config()
        
        # Connect overlay callbacks
        self._setup_callbacks()
    
    def _load_saved_config(self):
        """Load saved HP/Mana regions from config."""
        config = self.config_manager.config
        
        if config.regions.hp_region:
            self.reader.set_regions(hp_region=config.regions.hp_region)
            self.overlay.set_hp_region_status(True, config.regions.hp_region)
            print(f"📍 Loaded HP region: {config.regions.hp_region}")
        
        if config.regions.mana_region:
            self.reader.set_regions(mana_region=config.regions.mana_region)
            self.overlay.set_mana_region_status(True, config.regions.mana_region)
            print(f"📍 Loaded Mana region: {config.regions.mana_region}")
        
        # Load healer config
        healer_cfg = config.healer
        self.healer.heal.enabled = healer_cfg.heal_enabled
        self.healer.heal.threshold = healer_cfg.heal_threshold
        self.healer.heal.hotkey = healer_cfg.heal_hotkey
        self.healer.critical_heal.enabled = healer_cfg.critical_enabled
        self.healer.critical_heal.threshold = healer_cfg.critical_threshold
        self.healer.critical_heal.hotkey = healer_cfg.critical_hotkey
        self.healer.mana_restore.enabled = healer_cfg.mana_enabled
        self.healer.mana_restore.threshold = healer_cfg.mana_threshold
        self.healer.mana_restore.hotkey = healer_cfg.mana_hotkey
        
        # Load eater config
        eater_cfg = config.eater
        self.eater.enabled = eater_cfg.enabled
        self.eater.set_food_type(eater_cfg.food_type)
        self.eater.hotkey = eater_cfg.hotkey
        
        # Load haste config
        haste_cfg = config.haste
        self.haste.enabled = haste_cfg.enabled
        self.haste.hotkey = haste_cfg.hotkey
        
        # Load skinner config
        skinner_cfg = config.skinner
        self.skinner.toggle(skinner_cfg.enabled)
        self.skinner.hotkey = skinner_cfg.hotkey
    
    def _setup_callbacks(self):
        """Connect overlay controls to bot functionality."""
        # Healer callbacks - mapped to persistent wrappers
        self.overlay.on_heal_toggle = self._on_heal_toggle
        self.overlay.on_critical_toggle = self._on_critical_toggle
        self.overlay.on_mana_toggle = self._on_mana_toggle
        self.overlay.on_heal_threshold_change = self._on_heal_threshold_change
        self.overlay.on_critical_threshold_change = self._on_critical_threshold_change
        self.overlay.on_mana_threshold_change = self._on_mana_threshold_change
        
        # Eater callbacks
        self.overlay.on_eater_toggle = self._on_eater_toggle
        self.overlay.on_food_type_change = self._on_food_type_change
        self.overlay.on_eater_hotkey_change = self._on_eater_hotkey_change
        
        # Haste callbacks
        self.overlay.on_haste_toggle = self._on_haste_toggle
        self.overlay.on_haste_hotkey_change = self._on_haste_hotkey_change
        
        # Skinner callbacks
        self.overlay.on_skinner_toggle = self._on_skinner_toggle
        self.overlay.on_skinner_hotkey_change = self._on_skinner_hotkey_change
        
        # Hotkey change callbacks
        self.overlay.on_heal_hotkey_change = self._on_heal_hotkey_change
        self.overlay.on_critical_hotkey_change = self._on_critical_hotkey_change
        self.overlay.on_mana_hotkey_change = self._on_mana_hotkey_change
        
        # Region selection callbacks
        self.overlay.on_hp_region_select = self._on_hp_region_selected
        self.overlay.on_mana_region_select = self._on_mana_region_selected
        self.overlay.on_reset_config = self._on_reset_config

    # Persistent Config Wrappers
    def _on_heal_toggle(self, enabled: bool):
        self.healer.toggle_heal(enabled)
        self.config_manager.config.healer.heal_enabled = enabled
        self.config_manager.save()
        
    def _on_critical_toggle(self, enabled: bool):
        self.healer.toggle_critical_heal(enabled)
        self.config_manager.config.healer.critical_enabled = enabled
        self.config_manager.save()
        
    def _on_mana_toggle(self, enabled: bool):
        self.healer.toggle_mana_restore(enabled)
        self.config_manager.config.healer.mana_enabled = enabled
        self.config_manager.save()
        
    def _on_eater_toggle(self, enabled: bool):
        self.eater.toggle(enabled)
        self.config_manager.config.eater.enabled = enabled
        self.config_manager.save()
        
    def _on_food_type_change(self, value: str):
        self.eater.set_food_type(value)
        self.config_manager.config.eater.food_type = value
        self.config_manager.save()
        
    def _on_eater_hotkey_change(self, key: str):
        self.eater.hotkey = key
        self.config_manager.config.eater.hotkey = key
        self.config_manager.save()
        
    def _on_haste_toggle(self, enabled: bool):
        self.haste.toggle(enabled)
        self.config_manager.config.haste.enabled = enabled
        self.config_manager.save()
        
    def _on_haste_hotkey_change(self, key: str):
        self.haste.hotkey = key
        self.config_manager.config.haste.hotkey = key
        self.config_manager.save()
    
    def _on_skinner_toggle(self, enabled: bool):
        self.skinner.toggle(enabled)
        self.config_manager.config.skinner.enabled = enabled
        self.config_manager.save()
        
    def _on_skinner_hotkey_change(self, key: str):
        self.skinner.hotkey = key
        self.config_manager.config.skinner.hotkey = key
        self.config_manager.save()
        
    def _on_heal_threshold_change(self, value: int):
        self.healer.set_heal_threshold(value)
        self.config_manager.config.healer.heal_threshold = value
        self.config_manager.save()
        
    def _on_critical_threshold_change(self, value: int):
        self.healer.set_critical_threshold(value)
        self.config_manager.config.healer.critical_threshold = value
        self.config_manager.save()
        
    def _on_mana_threshold_change(self, value: int):
        self.healer.set_mana_threshold(value)
        self.config_manager.config.healer.mana_threshold = value
        self.config_manager.save()
    
    def _on_hp_region_selected(self, region: tuple):
        """Handle HP region selection."""
        self.reader.set_regions(hp_region=region)
        self.config_manager.set_hp_region(region)
        print(f"📍 HP region saved: {region}")
    
    def _on_mana_region_selected(self, region: tuple):
        """Handle Mana region selection."""
        self.reader.set_regions(mana_region=region)
        self.config_manager.set_mana_region(region)
        print(f"📍 Mana region saved: {region}")
    
    def _on_reset_config(self):
        """Handle config reset."""
        self.config_manager.reset_regions()
        self.reader.set_regions(hp_region=None, mana_region=None)
        print("🔄 Regions reset")
    
    def _on_heal_hotkey_change(self, key: str):
        """Handle heal hotkey change."""
        self.healer.heal.hotkey = key
        self.config_manager.config.healer.heal_hotkey = key
        self.config_manager.save()
    
    def _on_critical_hotkey_change(self, key: str):
        """Handle critical heal hotkey change."""
        self.healer.critical_heal.hotkey = key
        self.config_manager.config.healer.critical_hotkey = key
        self.config_manager.save()
    
    def _on_mana_hotkey_change(self, key: str):
        """Handle mana hotkey change."""
        self.healer.mana_restore.hotkey = key
        self.config_manager.config.healer.mana_hotkey = key
        self.config_manager.save()
    
    def start(self):
        """Start the bot loop."""
        # Verify configuration
        if not self.reader.is_configured():
            self.overlay.show_error("⚠️ Configure HP/Mana regions first!")
            return False
        
        self.active = True
        self.skinner.start()  # Start listener
        self.overlay.set_status("🔍 Searching...")
        return True
    
    def stop(self):
        """Stop the bot loop."""
        self.active = False
        self.skinner.stop()  # Stop listener
        self.overlay.set_status("⏸️ Stopped")
        self.overlay.set_hp(None)
        self.overlay.set_mana(None)
    
    def _capture_screen(self) -> Image.Image:
        """Capture entire screen."""
        monitor = self.sct.monitors[1]  # Primary monitor
        screenshot = self.sct.grab(monitor)
        return Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
    
    def run_loop(self):
        """Main bot loop - runs in background."""
        import traceback
        wait = 1.0 / REFRESH_RATE
        
        while self.running:
            try:
                # Check Auto Eater overlapping Auto Haste (both time based)
                if self.active:
                    self.eater.check_and_eat()
                    self.haste.check_and_cast()
                    # auto skinner runs in its own thread via listener

                # Only read if regions are configured
                if not self.reader.is_configured():
                    time.sleep(0.5)
                    continue
                
                # Capture screen
                img = self._capture_screen()
                
                # Read HP/Mana from configured regions
                status = self.reader.read_status(img)
                
                # Always update display (even when not active)
                if status.hp_current or status.mana_current:
                    self.overlay.set_hp(status.hp_current, status.hp_max)
                    self.overlay.set_mana(status.mana_current, status.mana_max)
                    
                    # Set max HP/Mana for healer
                    if status.hp_max and self.healer.max_hp is None:
                        self.healer.set_max_hp(status.hp_max)
                    if status.mana_max and self.healer.max_mana is None:
                        self.healer.set_max_mana(status.mana_max)
                    
                    # Set status based on app state
                    if self.active:
                        self.overlay.set_status("✅ Running")
                        
                        # Perform healing actions (silently)
                        heal_result = None
                        mana_result = False
                        
                        if status.hp_current:
                            heal_result = self.healer.check_and_heal(status.hp_current)
                        
                        if not heal_result and status.mana_current:
                            mana_result = self.healer.check_and_restore_mana(status.mana_current)
                    else:
                        self.overlay.set_status("⏸️ Monitoring")
                else:
                    self.overlay.set_status("🔍 Reading...")
                
                time.sleep(wait)
                
            except Exception as e:
                print(f"❌ ERROR: {e}")
                traceback.print_exc()
                self.overlay.set_status(f"❌ Error: {str(e)[:20]}")
                time.sleep(1)
    
    def run(self):
        """Start bot with overlay."""
        self.running = True
        
        # Start bot loop in background thread
        bot_thread = threading.Thread(target=self.run_loop, daemon=True)
        bot_thread.start()
        
        # Run overlay in main thread
        self.overlay.create_window()
        
        # Set loaded config in UI (after window is created)
        config = self.config_manager.config
        
        # Set region status
        if config.regions.hp_region:
            self.overlay.set_hp_region_status(True, config.regions.hp_region)
        if config.regions.mana_region:
            self.overlay.set_mana_region_status(True, config.regions.mana_region)
        
        # Set hotkeys
        self.overlay.set_hotkeys(
            config.healer.heal_hotkey,
            config.healer.critical_hotkey, 
            config.healer.mana_hotkey
        )
        
        # Manually set eater/haste hotkey since it's separate
        if self.overlay.eater_hotkey_var:
             self.overlay.eater_hotkey_var.set(config.eater.hotkey)
        if self.overlay.haste_hotkey_var:
             self.overlay.haste_hotkey_var.set(config.haste.hotkey)
        if self.overlay.skinner_hotkey_var:
             self.overlay.skinner_hotkey_var.set(config.skinner.hotkey)
             
        # Set food type
        if self.overlay.food_type_var:
            self.overlay.food_type_var.set(config.eater.food_type)
        
        # Set persistent values in UI
        if self.overlay.heal_enabled: self.overlay.heal_enabled.set(config.healer.heal_enabled)
        if self.overlay.critical_enabled: self.overlay.critical_enabled.set(config.healer.critical_enabled)
        if self.overlay.mana_enabled: self.overlay.mana_enabled.set(config.healer.mana_enabled)
        if self.overlay.eater_enabled: self.overlay.eater_enabled.set(config.eater.enabled)
        if self.overlay.haste_enabled: self.overlay.haste_enabled.set(config.haste.enabled)
        if self.overlay.skinner_enabled: self.overlay.skinner_enabled.set(config.skinner.enabled)
        
        if self.overlay.heal_threshold_var: self.overlay.heal_threshold_var.set(str(config.healer.heal_threshold))
        if self.overlay.critical_threshold_var: self.overlay.critical_threshold_var.set(str(config.healer.critical_threshold))
        if self.overlay.mana_threshold_var: self.overlay.mana_threshold_var.set(str(config.healer.mana_threshold))
        
        # Start mainloop
        self.overlay.root.mainloop()
        
        # Cleanup
        self.running = False
        self.sct.close()


def main():
    import pytesseract
    
    # Initialize config manager
    config_manager = ConfigManager()
    config_manager.load()

    # WINDOWS FIX: Auto-detect Tesseract path if not in PATH
    if platform.system() == "Windows":
        import shutil
        if not shutil.which("tesseract"):
            # Check common default install locations
            common_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Users\%USERNAME%\AppData\Local\Tesseract-OCR\tesseract.exe"
            ]
            import os
            for p in common_paths:
                expanded = os.path.expandvars(p)
                if os.path.exists(expanded):
                    print(f"🔍 Found Tesseract manually at: {expanded}")
                    pytesseract.pytesseract.tesseract_cmd = expanded
                    break

    try:
        pytesseract.get_tesseract_version()
    except:
        if platform.system() == "Darwin":
            print("⚠️ Tesseract not found! Install: brew install tesseract")
        elif platform.system() == "Windows":
             print("⚠️ Tesseract not found! Install Tesseract-OCR and add to PATH.")
        else:
             print("⚠️ Tesseract not found! Install tesseract-ocr package.")
        return
    overlay = TibiaStyleOverlay()
    bot = TibiaBot(overlay, config_manager)
    
    overlay.on_start = bot.start
    overlay.on_stop = bot.stop
    
    print(f"Starting Windify Helper...")
    bot.run()


if __name__ == "__main__":
    main()
