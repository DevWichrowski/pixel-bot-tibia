"""
Tibia Pixel Bot - Main with Overlay
"""

import time
import threading
from config import BOT_NAME, REFRESH_RATE
from window_finder import WindowTracker
from screen_capture import ScreenCapture
from hp_mana_reader import HPManaReader
from overlay import BotOverlay


class TibiaBot:
    def __init__(self, overlay: BotOverlay):
        self.overlay = overlay
        self.tracker = WindowTracker()
        self.capture = ScreenCapture()
        self.reader = HPManaReader()
        self.running = False
        self.active = False
    
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
                    self.overlay.set_status("✅ Running")
                    self.overlay.set_hp(status.hp)
                    self.overlay.set_mana(status.mana)
                else:
                    self.overlay.set_status("🔍 Reading...")
            
            time.sleep(wait)
    
    def run(self):
        """Start bot with overlay."""
        self.running = True
        
        # Start bot loop in background thread
        bot_thread = threading.Thread(target=self.run_loop, daemon=True)
        bot_thread.start()
        
        # Run overlay in main thread (tkinter requirement)
        self.overlay.run()
        
        # Cleanup
        self.running = False
        self.capture.close()


def main():
    # Check tesseract
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
    except:
        print("⚠️ Tesseract not found! Install: brew install tesseract")
        return
    
    # Create overlay with callbacks
    overlay = BotOverlay()
    bot = TibiaBot(overlay)
    
    overlay.on_start = bot.start
    overlay.on_stop = bot.stop
    
    print(f"Starting {BOT_NAME} with overlay...")
    bot.run()


if __name__ == "__main__":
    main()
