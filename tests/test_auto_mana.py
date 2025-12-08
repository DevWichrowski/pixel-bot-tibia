import unittest
from unittest.mock import MagicMock
import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from healer import AutoHealer

class TestAutoMana(unittest.TestCase):
    
    def setUp(self):
        self.mock_press = MagicMock()
        self.healer = AutoHealer(self.mock_press)
        
        # Configuration
        self.healer.set_max_mana(1000)
        self.healer.mana_restore.enabled = True
        self.healer.mana_restore.threshold = 60  # 600 Mana
        self.healer.mana_restore.hotkey = "F4"
        
        # Reset timestamps
        self.healer.mana_restore.last_cast = 0

    def test_mana_trigger_below_threshold(self):
        """Should restore mana when Mana < threshold."""
        # 500 < 600 (60%)
        result = self.healer.check_and_restore_mana(500)
        self.assertTrue(result)
        self.mock_press.assert_called_with("F4")

    def test_mana_not_trigger_above_threshold(self):
        """Should NOT restore mana when Mana > threshold."""
        # 700 > 600 (60%)
        result = self.healer.check_and_restore_mana(700)
        self.assertFalse(result)
        self.mock_press.assert_not_called()

    def test_mana_trigger_exact_threshold(self):
        """Should NOT restore mana exactly AT threshold."""
        # 600 == 600 (60%) -> False
        result = self.healer.check_and_restore_mana(600)
        self.assertFalse(result)
        self.mock_press.assert_not_called()
        
        # 599 < 600 -> True
        result = self.healer.check_and_restore_mana(599)
        self.assertTrue(result)

    def test_mana_disabled(self):
        """Should not action if disabled."""
        self.healer.mana_restore.enabled = False
        result = self.healer.check_and_restore_mana(100)
        self.assertFalse(result)
        self.mock_press.assert_not_called()

    def test_mana_cooldown(self):
        """Should respect cooldown."""
        # 1. Cast
        self.healer.check_and_restore_mana(500)
        self.mock_press.assert_called_with("F4")
        self.mock_press.reset_mock()
        
        # 2. Immediate recast -> Block
        result = self.healer.check_and_restore_mana(500)
        self.assertFalse(result)
        self.mock_press.assert_not_called()

    def test_global_cooldown_interaction(self):
        """Mana should respect global cooldown from healing."""
        # This depends on implementation. Does Mana share global CD with Heal?
        # healer.py source check: 
        # autohealer uses single last_cast_time for everything
        
        # Simulate recent heal
        self.healer.last_cast_time = time.time()
        
        # Try Mana
        result = self.healer.check_and_restore_mana(500)
        
        # Should be blocked by global cooldown
        self.assertFalse(result)
        self.mock_press.assert_not_called()

if __name__ == '__main__':
    unittest.main()
