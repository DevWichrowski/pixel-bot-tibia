import time
import random
from typing import Callable, Optional

class AutoHaste:
    def __init__(self, press_key_callback: Callable[[str], None]):
        self.press_key = press_key_callback
        self.enabled = False
        self.hotkey = "x"
        self.next_cast_time = 0.0
        
    def toggle(self, enabled: bool):
        self.enabled = enabled
        if enabled:
            # Schedule next cast in 31-33 seconds (DO NOT cast immediately)
            delay = random.uniform(31.0, 33.0)
            self.next_cast_time = time.time() + delay
            
            next_time_str = time.strftime("%H:%M:%S", time.localtime(self.next_cast_time))
            print(f"⚡ Auto Haste ENABLED (Hotkey: {self.hotkey}). First cast at {next_time_str} (in {delay:.1f}s)")
        else:
            print("⚡ Auto Haste DISABLED")
            
    def check_and_cast(self):
        """Check if it's time to cast haste."""
        if not self.enabled:
            return

        if time.time() >= self.next_cast_time:
            self._cast_now()
            
    def _cast_now(self):
        """Cast haste and schedule next."""
        self.press_key(self.hotkey)
        
        # Schedule next cast in 31-33 seconds
        delay = random.uniform(31.0, 33.0)
        self.next_cast_time = time.time() + delay
        
        # Calculate human readable time
        next_time_str = time.strftime("%H:%M:%S", time.localtime(self.next_cast_time))
        print(f"⚡ Cast Haste. Next cast at {next_time_str} (in {delay:.1f}s)")
