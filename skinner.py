import time
import random
import threading
from typing import Callable
from pynput import mouse

class AutoSkinner:
    """
    Listens for right mouse clicks and triggers a hotkey press.
    Used for skinning monsters automatically after looting.
    """
    
    def __init__(self, press_key_callback: Callable[[str], None]):
        self.press_key = press_key_callback
        self.enabled = False
        self.hotkey = "["
        self.listener = None
        self._running = False

    def start(self):
        """Start the mouse listener."""
        if not self._running:
            self.listener = mouse.Listener(on_click=self._on_click)
            self.listener.start()
            self._running = True
            print("🔪 Skinner listener started")

    def stop(self):
        """Stop the mouse listener."""
        if self.listener:
            self.listener.stop()
            self.listener = None
        self._running = False
        print("🔪 Skinner listener stopped")

    def toggle(self, enabled: bool):
        """Enable/Disable logic (listener keeps running)."""
        self.enabled = enabled
        status = "ENABLED" if enabled else "DISABLED"
        print(f"🔪 Auto Skinner {status} (Hotkey: {self.hotkey})")

    def _on_click(self, x, y, button, pressed):
        """Handle mouse clicks."""
        # Only react to right button press (not release) and if enabled
        if self.enabled and pressed and button == mouse.Button.right:
             # Run in separate thread to not block listener
             threading.Thread(target=self._perform_skinning, daemon=True).start()

    def _perform_skinning(self):
        """Wait delay and press hotkey."""
        delay = random.uniform(0.2, 0.4)
        time.sleep(delay)
        
        self.press_key(self.hotkey)
        print(f"🔪 Skinned! (in {delay:.3f}s)")
