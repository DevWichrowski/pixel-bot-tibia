"""
Tibia Pixel Bot - Main
Monitors HP and Mana in real-time.
"""

import time
from config import BOT_NAME, REFRESH_RATE, DEBUG_MODE
from window_finder import WindowTracker
from screen_capture import ScreenCapture
from hp_mana_reader import HPManaReader


class TibiaBot:
    def __init__(self):
        self.tracker = WindowTracker()
        self.capture = ScreenCapture()
        self.reader = HPManaReader()
        self.running = False
    
    def run(self):
        print(f"\n{'='*40}")
        print(f"  {BOT_NAME}")
        print(f"  {REFRESH_RATE} FPS")
        print(f"{'='*40}\n")
        
        self.running = True
        wait = 1.0 / REFRESH_RATE
        
        try:
            while self.running:
                window = self.tracker.update()
                
                if not window:
                    print("\r⚠️  Tibia not found...", end="", flush=True)
                    time.sleep(0.5)
                    continue
                
                if self.tracker.has_changed():
                    self.reader.reset()
                    if DEBUG_MODE:
                        print(f"\n📐 Window: {window['width']}x{window['height']}")
                
                img = self.capture.capture_window(window)
                if img:
                    status = self.reader.read_status(img)
                    if status.hp or status.mana:
                        hp = status.hp or "?"
                        mana = status.mana or "?"
                        print(f"\r❤️ HP: {hp:>5}  |  🔷 Mana: {mana:>5}", end="", flush=True)
                
                time.sleep(wait)
        
        except KeyboardInterrupt:
            print("\n\n👋 Stopped")
        finally:
            self.capture.close()


def main():
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
    except:
        print("⚠️ Tesseract not found! Install: brew install tesseract")
        return
    
    TibiaBot().run()


if __name__ == "__main__":
    main()
