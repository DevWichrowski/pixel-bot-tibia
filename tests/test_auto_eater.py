import unittest
from unittest.mock import MagicMock, patch, call
import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eater import AutoEater

class TestAutoEater(unittest.TestCase):
    
    def setUp(self):
        self.mock_press = MagicMock()
        self.eater = AutoEater(self.mock_press)
        self.eater.enabled = True
        self.eater.hotkey = "]"
        self.eater.next_eat_time = 0

    def test_eat_sequence(self):
        """Should eat twice."""
        with patch('time.sleep') as mock_sleep:
            self.eater.check_and_eat()
            
            # Expect 2 calls
            self.assertEqual(self.mock_press.call_count, 2)
            self.mock_press.assert_has_calls([call("]"), call("]")])

    def test_fire_mushroom_duration(self):
        """Fire Mushroom duration logic."""
        self.eater.set_food_type("fire_mushroom") # 432s
        self.eater.next_eat_time = 0
        
        with patch('time.sleep'), patch('time.time', return_value=1000):
            self.eater.check_and_eat()
            
            # Logic: 2 items -> 432 * 2 = 864s duration.
            # Next time = 1000 + 864 + random(1-6)
            min_next = 1000 + 864 + 1
            max_next = 1000 + 864 + 6
            
            self.assertGreaterEqual(self.eater.next_eat_time, min_next)
            self.assertLessEqual(self.eater.next_eat_time, max_next)

    def test_brown_mushroom_duration(self):
        """Brown Mushroom duration logic."""
        self.eater.set_food_type("brown_mushroom") # 264s
        self.eater.next_eat_time = 0
        
        with patch('time.sleep'), patch('time.time', return_value=1000):
            self.eater.check_and_eat()
            
            # Logic: 264 * 2 = 528s duration.
            min_next = 1000 + 528 + 1
            max_next = 1000 + 528 + 6
            
            self.assertGreaterEqual(self.eater.next_eat_time, min_next)
            self.assertLessEqual(self.eater.next_eat_time, max_next)

    def test_switch_food_resets_logic(self):
        """Switching food type updates current food."""
        self.eater.set_food_type("fire_mushroom")
        self.assertEqual(self.eater.current_food, "fire_mushroom")
        
        self.eater.set_food_type("brown_mushroom")
        self.assertEqual(self.eater.current_food, "brown_mushroom")
        
        # Should reset immediate eat timer?
        # Implementation choice in eater.py was: self.next_eat_time = 0.0
        self.assertEqual(self.eater.next_eat_time, 0.0)

    def test_disabled_no_action(self):
        self.eater.enabled = False
        self.eater.check_and_eat()
        self.mock_press.assert_not_called()

    def test_timer_future(self):
        """Should NOT eat if timer is in future."""
        # Set next eat time to future
        self.eater.next_eat_time = time.time() + 100
        
        self.eater.check_and_eat()
        self.mock_press.assert_not_called()

if __name__ == '__main__':
    unittest.main()
