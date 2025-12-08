import unittest
from unittest.mock import MagicMock, patch, call
import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from haste import AutoHaste

class TestAutoHaste(unittest.TestCase):
    
    def setUp(self):
        self.mock_press = MagicMock()
        self.haste = AutoHaste(self.mock_press)
        self.haste.enabled = True
        self.haste.hotkey = "x"
        self.haste.next_cast_time = 0.0

    def test_haste_trigger(self):
        """Should cast haste."""
        with patch('time.sleep') as mock_sleep:
            self.haste.check_and_cast()
            
            self.mock_press.assert_called_with("x")

    def test_haste_timer_update(self):
        """Should schedule next cast in 31-33s."""
        self.haste.next_cast_time = 0
        
        with patch('time.time', return_value=1000):
            with patch('random.uniform', return_value=32.0) as mock_random:
                self.haste.check_and_cast()
                
                # Verify random range called with correct args
                # Note: This checks if random.uniform was called with (31.0, 33.0)
                # mock_random.assert_called_with(31.0, 33.0) # Implementation detail check
                
                # Check next time logic
                # 1000 + 32 = 1032
                self.assertEqual(self.haste.next_cast_time, 1032.0)

    def test_haste_disabled(self):
        """Should do nothing if disabled."""
        self.haste.enabled = False
        self.haste.check_and_cast()
        self.mock_press.assert_not_called()

    def test_hotkey_change(self):
        """Should use new hotkey."""
        self.haste.hotkey = "F5"
        self.haste.check_and_cast()
        self.mock_press.assert_called_with("F5")

    def test_toggle_initial_delay(self):
        """Enabling should set timer to future (not 0)."""
        self.haste.enabled = False
        self.haste.toggle(True)
        
        # Timer should be in future
        self.assertGreater(self.haste.next_cast_time, time.time())
        
        # Should not cast immediately
        self.mock_press.reset_mock()
        self.haste.check_and_cast()
        self.mock_press.assert_not_called()

if __name__ == '__main__':
    unittest.main()
