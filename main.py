"""
Windify Bot - Main with Overlay and Auto-Heal
"""

import time
import threading
from config import BOT_NAME, REFRESH_RATE
from window_finder import WindowTracker
from screen_capture import ScreenCapture
from hp_mana_reader import HPManaReader
from overlay import BotOverlay
from healer import AutoHealer, press_key


class TibiaBot:
    def __init__(self, overlay: BotOverlay):
        self.overlay = overlay
        self.tracker = WindowTracker()
        self.capture = ScreenCapture()
        self.reader = HPManaReader()
        self.healer = AutoHealer(press_key)
        self.running = False
        self.active = False
        
        # Connect overlay callbacks
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """Connect overlay controls to healer."""
        self.overlay.on_heal_toggle = self.healer.toggle_heal
        self.overlay.on_critical_toggle = self.healer.toggle_critical_heal
        self.overlay.on_heal_threshold_change = self.healer.set_heal_threshold
        self.overlay.on_critical_threshold_change = self.healer.set_critical_threshold
        self.overlay.on_max_hp_change = self.healer.set_max_hp
    
    def start(self):
        """Start the bot loop."""
        self.active = True
        self.overlay.set_status("🔍 Searching...")
    
    def stop(self):
        """Stop the bot loop."""
        self.active = False
        self.overlay.set_status("⏸️ Stopped")
        self.overlay.set_hp(None)
        self.overlay.set_mana(None)
    
    def run_loop(self):
        """Main bot loop - runs in background."""
        wait = 1.0 / REFRESH_RATE
        
        while self.running:
            if not self.active:
                time.sleep(0.1)
                continue
            
            window = self.tracker.update()
            
            if not window:
                self.overlay.set_status("⚠️ Tibia not found")
                time.sleep(0.5)
                continue
            
            if self.tracker.has_changed():
                self.reader.reset()
            
            img = self.capture.capture_window(window)
            if img:
                status = self.reader.read_status(img)
                
                if status.hp or status.mana:
                    self.overlay.set_hp(status.hp)
                    self.overlay.set_mana(status.mana)
                    
                    # Auto-detect max HP and update overlay
                    if status.hp and self.healer.max_hp is None:
                        self.healer.auto_detect_max_hp(status.hp)
                        self.overlay.set_max_hp(self.healer.max_hp)
                    
                    # Check for healing
                    if status.hp:
                        heal_result = self.healer.check_and_heal(status.hp)
                        
                        if heal_result == "critical":
                            self.overlay.set_status("🩹 Critical Heal!")
                        elif heal_result == "normal":
                            self.overlay.set_status("🩹 Healed!")
                        elif self.healer.is_on_cooldown():
                            cd = self.healer.get_cooldown_remaining()
                            self.overlay.set_status(f"✅ Running (CD: {cd:.1f}s)")
                        else:
                            hp_pct = self.healer.get_hp_percent(status.hp)
                            self.overlay.set_status(f"✅ Running ({hp_pct:.0f}% HP)")
                else:
                    self.overlay.set_status("🔍 Reading...")
            
            time.sleep(wait)
    
    def run(self):
        """Start bot with overlay."""
        self.running = True
        
        # Start bot loop in background thread
        bot_thread = threading.Thread(target=self.run_loop, daemon=True)
        bot_thread.start()
        
        # Run overlay in main thread
        self.overlay.run()
        
        # Cleanup
        self.running = False
        self.capture.close()


def main():
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
    except:
        print("⚠️ Tesseract not found! Install: brew install tesseract")
        return
    
    overlay = BotOverlay()
    bot = TibiaBot(overlay)
    
    overlay.on_start = bot.start
    overlay.on_stop = bot.stop
    
    print(f"Starting {BOT_NAME} with overlay...")
    bot.run()


if __name__ == "__main__":
    main()
