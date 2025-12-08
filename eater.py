"""
Windify Bot - Auto Eater
Handles automatic food consumption.
"""

import time
import random
from dataclasses import dataclass
from typing import Callable, Optional

@dataclass
class FoodType:
    name: str
    duration: int  # Duration in seconds for one item

class AutoEater:
    """
    Manages auto eating.
    Logic: Eats 2 items -> waits (duration * 2) + random delay.
    """
    
    # Food Definitions
    FOODS = {
        "fire_mushroom": FoodType("Fire Mushroom", 432),
        "brown_mushroom": FoodType("Brown Mushroom", 264)
    }
    
    def __init__(self, press_key_callback: Callable[[str], None]):
        self.press_key = press_key_callback
        self.enabled = False
        self.hotkey = "]"
        self.current_food = "fire_mushroom"  # Default
        self.next_eat_time = 0.0
    
    def set_food_type(self, food_key: str):
        """Set the type of food to eat."""
        if food_key in self.FOODS:
            self.current_food = food_key
            print(f"🍖 Food set to: {self.FOODS[food_key].name} ({self.FOODS[food_key].duration}s)")
            # Reset timer so we eat immediately/soon after changing type?
            # Or keep existing timer? Let's eat immediately to be safe.
            self.next_eat_time = 0.0
    
    def toggle(self, enabled: bool):
        """Enable/Disable auto eater."""
        self.enabled = enabled
        if enabled:
            # When enabling, eat immediately
            self.next_eat_time = 0.0
            print("🍖 Auto Eater enabled")
        else:
            print("🍖 Auto Eater disabled")
            
    def check_and_eat(self):
        """Check if it's time to eat, and eat if so."""
        if not self.enabled:
            return
            
        now = time.time()
        if now >= self.next_eat_time:
            self._eat_now()
            
    def _eat_now(self):
        """Perform the eating action and set next timer."""
        # Press hotkey twice with interval
        self.press_key(self.hotkey)
        time.sleep(random.uniform(0.2, 0.4))
        self.press_key(self.hotkey)
        
        # Calculate wait time
        food = self.FOODS[self.current_food]
        duration = food.duration * 2  # We ate 2 items
        
        # Add random delay (1-6s)
        delay = duration + random.uniform(1.0, 6.0)
        
        self.next_eat_time = time.time() + delay
        
        # Format next eat time for display
        next_time_str = time.strftime("%H:%M:%S", time.localtime(self.next_eat_time))
        print(f"🍖 Ate 2x {food.name}. Next meal at {next_time_str} (in {int(delay)}s)")

