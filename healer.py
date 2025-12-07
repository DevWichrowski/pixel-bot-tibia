"""
Windify Bot - Auto Healer
Handles automatic healing based on HP thresholds.
"""

import time
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class HealConfig:
    """Configuration for a heal type."""
    enabled: bool = False
    threshold: int = 75  # Heal when HP drops below this %
    hotkey: str = "F1"


class AutoHealer:
    """
    Manages auto-healing with two heal types:
    - Normal Heal (default 75%, F1)
    - Critical Heal (default 50%, F2)
    
    Has 1 second global cooldown between any spell.
    """
    
    COOLDOWN = 1.0  # 1 second cooldown
    
    def __init__(self, press_key_callback: Callable[[str], None]):
        """
        Args:
            press_key_callback: Function to press a hotkey, e.g. press_key("F1")
        """
        self.press_key = press_key_callback
        
        # Max HP (auto-detected or manually set)
        self.max_hp: Optional[int] = None
        
        # Heal configurations
        self.heal = HealConfig(enabled=False, threshold=75, hotkey="F1")
        self.critical_heal = HealConfig(enabled=False, threshold=50, hotkey="F2")
        
        # Cooldown tracking
        self.last_cast_time = 0.0
    
    def set_max_hp(self, value: int):
        """Set max HP manually."""
        if value > 0:
            self.max_hp = value
    
    def auto_detect_max_hp(self, current_hp: int):
        """Auto-detect max HP from first reading (if not set)."""
        if self.max_hp is None and current_hp and current_hp > 0:
            self.max_hp = current_hp
            print(f"📊 Max HP auto-detected: {self.max_hp}")
    
    def get_hp_percent(self, current_hp: int) -> float:
        """Calculate HP percentage."""
        if not self.max_hp or not current_hp:
            return 100.0
        return (current_hp / self.max_hp) * 100
    
    def is_on_cooldown(self) -> bool:
        """Check if we're still on cooldown."""
        return (time.time() - self.last_cast_time) < self.COOLDOWN
    
    def get_cooldown_remaining(self) -> float:
        """Get remaining cooldown time in seconds."""
        elapsed = time.time() - self.last_cast_time
        remaining = self.COOLDOWN - elapsed
        return max(0, remaining)
    
    def check_and_heal(self, current_hp: int) -> Optional[str]:
        """
        Check if healing is needed and cast if possible.
        
        Returns the heal type used ("critical", "normal") or None.
        """
        # Auto-detect max HP
        self.auto_detect_max_hp(current_hp)
        
        if not self.max_hp:
            return None
        
        # Check cooldown
        if self.is_on_cooldown():
            return None
        
        hp_percent = self.get_hp_percent(current_hp)
        
        # Critical heal has priority (lower threshold = more urgent)
        if self.critical_heal.enabled and hp_percent < self.critical_heal.threshold:
            self._cast_heal(self.critical_heal)
            return "critical"
        
        # Normal heal
        if self.heal.enabled and hp_percent < self.heal.threshold:
            self._cast_heal(self.heal)
            return "normal"
        
        return None
    
    def _cast_heal(self, config: HealConfig):
        """Cast a heal spell."""
        self.press_key(config.hotkey)
        self.last_cast_time = time.time()
        print(f"🩹 Cast heal: {config.hotkey} (threshold: {config.threshold}%)")
    
    # Toggle methods for overlay
    def toggle_heal(self, enabled: bool):
        self.heal.enabled = enabled
    
    def toggle_critical_heal(self, enabled: bool):
        self.critical_heal.enabled = enabled
    
    def set_heal_threshold(self, value: int):
        if 1 <= value <= 99:
            self.heal.threshold = value
    
    def set_critical_threshold(self, value: int):
        if 1 <= value <= 99:
            self.critical_heal.threshold = value


def press_key(key: str):
    """Press a keyboard key using macOS."""
    import subprocess
    
    # Map F-keys to keycodes
    keycodes = {
        "F1": 122, "F2": 120, "F3": 99, "F4": 118,
        "F5": 96, "F6": 97, "F7": 98, "F8": 100,
        "F9": 101, "F10": 109, "F11": 103, "F12": 111,
    }
    
    keycode = keycodes.get(key.upper())
    if keycode:
        script = f'''
        tell application "System Events"
            key code {keycode}
        end tell
        '''
        subprocess.run(["osascript", "-e", script], capture_output=True)


# Test
if __name__ == "__main__":
    healer = AutoHealer(press_key)
    healer.heal.enabled = True
    healer.heal.threshold = 75
    
    # Simulate HP readings
    healer.auto_detect_max_hp(1000)  # Max HP = 1000
    
    print(f"HP 100%: {healer.get_hp_percent(1000):.0f}%")
    print(f"HP 70%: {healer.get_hp_percent(700):.0f}%")
    
    # Should trigger heal at 70% (below 75%)
    result = healer.check_and_heal(700)
    print(f"Heal result: {result}")
