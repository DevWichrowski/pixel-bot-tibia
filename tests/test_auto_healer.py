import unittest
from unittest.mock import MagicMock
import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from healer import AutoHealer

class TestAutoHealer(unittest.TestCase):
    
    def setUp(self):
        self.mock_press = MagicMock()
        self.healer = AutoHealer(self.mock_press)
        
        # Configuration
        self.healer.set_max_hp(1000)
        self.healer.heal.enabled = True
        self.healer.critical_heal.enabled = True
        
        self.healer.heal.threshold = 75  # 750 HP
        self.healer.critical_heal.threshold = 50  # 500 HP
        self.healer.heal.hotkey = "F1"
        self.healer.critical_heal.hotkey = "F2"
        
        # Reset timestamps
        self.healer.heal.last_cast = 0
        self.healer.critical_heal.last_cast = 0

    def test_heal_trigger_below_threshold(self):
        """Should heal when HP < threshold."""
        # 700 < 750 (75%)
        result = self.healer.check_and_heal(700)
        self.assertEqual(result, "normal")
        self.mock_press.assert_called_with("F1")

    def test_heal_not_trigger_above_threshold(self):
        """Should NOT heal when HP > threshold."""
        # 800 > 750 (75%)
        result = self.healer.check_and_heal(800)
        self.assertIsNone(result)
        self.mock_press.assert_not_called()

    def test_heal_trigger_exact_threshold(self):
        """Should NOT heal exactly AT threshold (logic is <)."""
        # 750 == 750 (75%)
        # Logic is usually: if current < max * (thresh/100)
        # 1000 * 0.75 = 750. If current is 750, 750 < 750 is FALSE.
        result = self.healer.check_and_heal(750)
        self.assertIsNone(result)
        self.mock_press.assert_not_called()
        
        # 749 < 750 -> Should heal
        result = self.healer.check_and_heal(749)
        self.assertEqual(result, "normal")

    def test_critical_priority(self):
        """Critical heal should take priority over normal heal."""
        # 400 < 500 (50% Critical) AND 400 < 750 (75% Normal)
        # Should initiate critical
        result = self.healer.check_and_heal(400)
        self.assertEqual(result, "critical")
        self.mock_press.assert_called_with("F2")
        
        # Ensure F1 NOT called
        # mock_press calls: [call('F2')]
        self.assertEqual(self.mock_press.call_count, 1)

    def test_critical_disabled(self):
        """If critical is disabled, normal heal should cover low HP."""
        self.healer.critical_heal.enabled = False
        
        # 400 HP (Low). Critical disabled. Should trigger Normal.
        result = self.healer.check_and_heal(400)
        self.assertEqual(result, "normal")
        self.mock_press.assert_called_with("F1")

    def test_heal_disabled(self):
        """If healing is disabled, nothing should happen."""
        self.healer.heal.enabled = False
        self.healer.critical_heal.enabled = False
        
        result = self.healer.check_and_heal(100)
        self.assertIsNone(result)
        self.mock_press.assert_not_called()

    def test_cooldown_logic(self):
        """Should respect cooldowns."""
        # 1. Cast heal
        self.healer.check_and_heal(700)
        self.mock_press.assert_called_with("F1")
        self.mock_press.reset_mock()
        
        # 2. Try immediate recast (should fail)
        result = self.healer.check_and_heal(700)
        self.assertIsNone(result)
        self.mock_press.assert_not_called()
        
        # 3. Wait for cooldown matches
        # We manually modify last_cast to simulate time passing
        self.healer.last_cast_time = 0  # Reset global cooldown
        
        result = self.healer.check_and_heal(700)
        self.assertEqual(result, "normal")
        self.mock_press.assert_called_with("F1")

    def test_max_hp_none(self):
        """Should handle case where Max HP is not set yet."""
        self.healer.max_hp = None
        result = self.healer.check_and_heal(700)
        self.assertIsNone(result)
        self.mock_press.assert_not_called()

if __name__ == '__main__':
    unittest.main()
