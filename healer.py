"""
Windify Bot - Auto Healer & Mana
Handles automatic healing and mana restoration based on thresholds.
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
    Manages auto-healing and mana:
    - Normal Heal (default 75%, F1)
    - Critical Heal (default 50%, F2)
    - Mana Restore (default 60%, F4)
    
    Has 1 second global cooldown between any spell.
    """
    
    COOLDOWN = 1.0  # 1 second cooldown
    
    def __init__(self, press_key_callback: Callable[[str], None]):
        """
        Args:
            press_key_callback: Function to press a hotkey, e.g. press_key("F1")
        """
        self.press_key = press_key_callback
        
        # Max HP and Mana (auto-detected or manually set)
        self.max_hp: Optional[int] = None
        self.max_mana: Optional[int] = None
        
        # Heal configurations - enabled by default
        self.heal = HealConfig(enabled=True, threshold=75, hotkey="F1")
        self.critical_heal = HealConfig(enabled=True, threshold=50, hotkey="F2")
        
        # Mana configuration - enabled by default
        self.mana_restore = HealConfig(enabled=True, threshold=60, hotkey="F4")
        
        # Critical heal is a potion mode - shares cooldown with mana, has priority
        self.critical_is_potion = False
        
        # Cooldown tracking
        self.last_cast_time = 0.0
    
    def set_max_hp(self, value: int):
        """Set max HP manually."""
        if value > 0:
            self.max_hp = value
    
    def set_max_mana(self, value: int):
        """Set max Mana manually."""
        if value > 0:
            self.max_mana = value
    
    def auto_detect_max_hp(self, current_hp: int):
        """Auto-detect max HP from first reading (if not set)."""
        if self.max_hp is None and current_hp and current_hp > 0:
            self.max_hp = current_hp
            print(f"📊 Max HP auto-detected: {self.max_hp}")
    
    def auto_detect_max_mana(self, current_mana: int):
        """Auto-detect max Mana from first reading (if not set)."""
        if self.max_mana is None and current_mana and current_mana > 0:
            self.max_mana = current_mana
            print(f"📊 Max Mana auto-detected: {self.max_mana}")
    
    def get_hp_percent(self, current_hp: int) -> float:
        """Calculate HP percentage."""
        if not self.max_hp or not current_hp:
            return 100.0
        return (current_hp / self.max_hp) * 100
    
    def get_mana_percent(self, current_mana: int) -> float:
        """Calculate Mana percentage."""
        if not self.max_mana or not current_mana:
            return 100.0
        return (current_mana / self.max_mana) * 100
    
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
    
    def toggle_mana_restore(self, enabled: bool):
        self.mana_restore.enabled = enabled
    
    def set_heal_threshold(self, value: int):
        if 1 <= value <= 99:
            self.heal.threshold = value
    
    def set_critical_threshold(self, value: int):
        if 1 <= value <= 99:
            self.critical_heal.threshold = value
    
    def set_mana_threshold(self, value: int):
        if 1 <= value <= 99:
            self.mana_restore.threshold = value
    
    def check_and_restore_mana(self, current_mana: int) -> bool:
        """
        Check if mana restore is needed and cast if possible.
        Returns True if mana was restored.
        """
        self.auto_detect_max_mana(current_mana)
        
        if not self.max_mana:
            return False
        
        if self.is_on_cooldown():
            return False
        
        mana_percent = self.get_mana_percent(current_mana)
        
        if self.mana_restore.enabled and mana_percent < self.mana_restore.threshold:
            self.press_key(self.mana_restore.hotkey)
            self.last_cast_time = time.time()
            print(f"🔷 Mana restore: {self.mana_restore.hotkey} (threshold: {self.mana_restore.threshold}%)")
            return True
        
        return False
    
    def check_critical_and_mana_with_priority(
        self, 
        current_hp: int, 
        current_mana: int
    ) -> tuple:
        """
        Check both critical heal and mana, with critical heal priority.
        
        This method should be used when critical_is_potion is True.
        Critical heal ALWAYS takes priority over mana restore because
        dying is worse than running out of mana.
        
        Returns:
            tuple: (heal_type or None, mana_restored: bool)
        """
        # Auto-detect max values
        self.auto_detect_max_hp(current_hp)
        self.auto_detect_max_mana(current_mana)
        
        if self.is_on_cooldown():
            return None, False
        
        # Calculate percentages
        hp_percent = self.get_hp_percent(current_hp) if current_hp and self.max_hp else 100.0
        mana_percent = self.get_mana_percent(current_mana) if current_mana and self.max_mana else 100.0
        
        # Priority 1: Critical heal (life-saving)
        if self.critical_heal.enabled and hp_percent < self.critical_heal.threshold:
            self._cast_heal(self.critical_heal)
            return "critical", False
        
        # Priority 2: Mana restore (only if critical heal not needed)
        if self.mana_restore.enabled and mana_percent < self.mana_restore.threshold:
            self.press_key(self.mana_restore.hotkey)
            self.last_cast_time = time.time()
            print(f"🔷 Mana restore: {self.mana_restore.hotkey} (threshold: {self.mana_restore.threshold}%)")
            return None, True
        
        return None, False


def press_key(key: str):
    """Press a keyboard key using pyautogui."""
    import pyautogui
    
    # Map key names if needed (pyautogui uses lowercase usually)
    key = key.lower()
    
    try:
        pyautogui.press(key)
    except Exception as e:
        print(f"Error pressing key {key}: {e}")


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
