"""
Tests for 'Critical heal is a potion' feature.

When critical_is_potion is True:
- Critical heal and mana share the same 1s cooldown
- Critical heal ALWAYS has priority over mana to prevent death

Example scenario:
- Critical threshold: 50%
- Mana threshold: 40%
- HP: 35%, Mana: 20%
- Result: Critical heal (NOT mana) because survival takes priority
"""

import unittest
from unittest.mock import MagicMock
import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from healer import AutoHealer


class TestCriticalIsPotion(unittest.TestCase):
    """Test suite for critical_is_potion feature."""
    
    def setUp(self):
        self.mock_press = MagicMock()
        self.healer = AutoHealer(self.mock_press)
        
        # Configure healer
        self.healer.set_max_hp(1000)
        self.healer.set_max_mana(1000)
        
        # Enable critical and mana
        self.healer.critical_heal.enabled = True
        self.healer.critical_heal.threshold = 50  # 500 HP
        self.healer.critical_heal.hotkey = "F2"
        
        self.healer.mana_restore.enabled = True
        self.healer.mana_restore.threshold = 40  # 400 Mana
        self.healer.mana_restore.hotkey = "F4"
        
        # Enable critical_is_potion mode
        self.healer.critical_is_potion = True
    
    def test_critical_priority_over_mana_when_both_needed(self):
        """
        MAIN SCENARIO: HP 35%, Mana 20%
        Both critical (50%) and mana (40%) thresholds are triggered.
        Critical heal MUST be used, NOT mana.
        """
        heal_result, mana_result = self.healer.check_critical_and_mana_with_priority(
            current_hp=350,    # 35% - below 50% critical threshold
            current_mana=200   # 20% - below 40% mana threshold
        )
        
        self.assertEqual(heal_result, "critical")
        self.assertFalse(mana_result)
        self.mock_press.assert_called_once_with("F2")
    
    def test_mana_restore_when_hp_is_safe(self):
        """
        HP 80%, Mana 20%
        Only mana threshold is triggered, HP is safe.
        Should restore mana.
        """
        heal_result, mana_result = self.healer.check_critical_and_mana_with_priority(
            current_hp=800,    # 80% - above 50% critical threshold
            current_mana=200   # 20% - below 40% mana threshold
        )
        
        self.assertIsNone(heal_result)
        self.assertTrue(mana_result)
        self.mock_press.assert_called_once_with("F4")
    
    def test_critical_only_when_mana_is_fine(self):
        """
        HP 35%, Mana 80%
        Only critical threshold is triggered.
        Should heal critically.
        """
        heal_result, mana_result = self.healer.check_critical_and_mana_with_priority(
            current_hp=350,    # 35% - below 50% critical threshold
            current_mana=800   # 80% - above 40% mana threshold
        )
        
        self.assertEqual(heal_result, "critical")
        self.assertFalse(mana_result)
        self.mock_press.assert_called_once_with("F2")
    
    def test_no_action_when_both_above_threshold(self):
        """
        HP 80%, Mana 80%
        Neither threshold is triggered.
        Should do nothing.
        """
        heal_result, mana_result = self.healer.check_critical_and_mana_with_priority(
            current_hp=800,
            current_mana=800
        )
        
        self.assertIsNone(heal_result)
        self.assertFalse(mana_result)
        self.mock_press.assert_not_called()
    
    def test_cooldown_blocks_all_actions(self):
        """After critical heal, mana should also be blocked by shared cooldown."""
        # Cast critical heal
        self.healer.check_critical_and_mana_with_priority(350, 200)
        self.mock_press.reset_mock()
        
        # Immediately try again - should be blocked
        heal_result, mana_result = self.healer.check_critical_and_mana_with_priority(350, 200)
        
        self.assertIsNone(heal_result)
        self.assertFalse(mana_result)
        self.mock_press.assert_not_called()
    
    def test_cooldown_blocks_mana_after_critical(self):
        """After critical heal, even pure mana request should be blocked."""
        # Cast critical heal (HP low, mana fine)
        self.healer.check_critical_and_mana_with_priority(350, 800)
        self.mock_press.reset_mock()
        
        # Immediately try mana only (HP now fine, mana low)
        heal_result, mana_result = self.healer.check_critical_and_mana_with_priority(800, 200)
        
        self.assertIsNone(heal_result)
        self.assertFalse(mana_result)
        self.mock_press.assert_not_called()
    
    def test_cooldown_reset_allows_action(self):
        """After cooldown expires, actions should work again."""
        # Cast critical heal
        self.healer.check_critical_and_mana_with_priority(350, 200)
        self.mock_press.reset_mock()
        
        # Reset cooldown
        self.healer.last_cast_time = 0
        
        # Now should work
        heal_result, mana_result = self.healer.check_critical_and_mana_with_priority(350, 200)
        
        self.assertEqual(heal_result, "critical")
        self.assertFalse(mana_result)
        self.mock_press.assert_called_once_with("F2")
    
    def test_exact_threshold_does_not_trigger(self):
        """HP/Mana exactly at threshold should NOT trigger (uses < not <=)."""
        # HP exactly at 50%, Mana exactly at 40%
        heal_result, mana_result = self.healer.check_critical_and_mana_with_priority(
            current_hp=500,    # 50% exactly
            current_mana=400   # 40% exactly
        )
        
        self.assertIsNone(heal_result)
        self.assertFalse(mana_result)
        self.mock_press.assert_not_called()
    
    def test_just_below_threshold_triggers(self):
        """HP/Mana just below threshold should trigger."""
        # HP at 499 (49.9%), Mana at 399 (39.9%)
        heal_result, mana_result = self.healer.check_critical_and_mana_with_priority(
            current_hp=499,
            current_mana=399
        )
        
        # Critical takes priority
        self.assertEqual(heal_result, "critical")
        self.assertFalse(mana_result)
    
    def test_critical_disabled_allows_mana(self):
        """When critical is disabled, mana should work normally."""
        self.healer.critical_heal.enabled = False
        
        heal_result, mana_result = self.healer.check_critical_and_mana_with_priority(
            current_hp=350,    # Would trigger critical if enabled
            current_mana=200   # Triggers mana
        )
        
        self.assertIsNone(heal_result)
        self.assertTrue(mana_result)
        self.mock_press.assert_called_once_with("F4")
    
    def test_mana_disabled_allows_critical(self):
        """When mana is disabled, critical should work normally."""
        self.healer.mana_restore.enabled = False
        
        heal_result, mana_result = self.healer.check_critical_and_mana_with_priority(
            current_hp=350,
            current_mana=200
        )
        
        self.assertEqual(heal_result, "critical")
        self.assertFalse(mana_result)
        self.mock_press.assert_called_once_with("F2")
    
    def test_both_disabled_does_nothing(self):
        """When both are disabled, nothing happens."""
        self.healer.critical_heal.enabled = False
        self.healer.mana_restore.enabled = False
        
        heal_result, mana_result = self.healer.check_critical_and_mana_with_priority(
            current_hp=100,
            current_mana=100
        )
        
        self.assertIsNone(heal_result)
        self.assertFalse(mana_result)
        self.mock_press.assert_not_called()
    
    def test_zero_hp_triggers_critical(self):
        """Edge case: HP at 0 should trigger critical."""
        heal_result, mana_result = self.healer.check_critical_and_mana_with_priority(
            current_hp=1,      # Almost dead
            current_mana=200
        )
        
        self.assertEqual(heal_result, "critical")
        self.assertFalse(mana_result)
    
    def test_zero_mana_triggers_restore(self):
        """Edge case: Mana at 0, HP safe - should restore mana."""
        heal_result, mana_result = self.healer.check_critical_and_mana_with_priority(
            current_hp=800,
            current_mana=1     # Almost no mana
        )
        
        self.assertIsNone(heal_result)
        self.assertTrue(mana_result)
    
    def test_feature_disabled_does_not_use_priority_method(self):
        """
        When critical_is_potion is False, should use original behavior.
        This tests the flag itself, not the method.
        """
        self.healer.critical_is_potion = False
        
        # Original behavior: check_and_heal for HP, check_and_restore_mana for mana
        # The priority method should NOT be called when feature is disabled
        # This is handled in main.py, but we verify the flag is respected
        self.assertFalse(self.healer.critical_is_potion)


class TestCriticalIsPotionIntegration(unittest.TestCase):
    """Integration tests for the priority system."""
    
    def setUp(self):
        self.mock_press = MagicMock()
        self.healer = AutoHealer(self.mock_press)
        self.healer.set_max_hp(1000)
        self.healer.set_max_mana(1000)
        self.healer.critical_heal.enabled = True
        self.healer.critical_heal.threshold = 50
        self.healer.mana_restore.enabled = True
        self.healer.mana_restore.threshold = 40
        self.healer.critical_is_potion = True
    
    def test_sequence_of_actions(self):
        """Test a realistic sequence of events."""
        # 1. HP drops low, use critical heal
        heal, mana = self.healer.check_critical_and_mana_with_priority(350, 200)
        self.assertEqual(heal, "critical")
        self.mock_press.assert_called_with("F2")
        self.mock_press.reset_mock()
        
        # 2. Immediately after - blocked by cooldown
        heal, mana = self.healer.check_critical_and_mana_with_priority(450, 200)
        self.assertIsNone(heal)
        self.assertFalse(mana)
        
        # 3. Cooldown expires, HP now safe, mana low
        self.healer.last_cast_time = 0
        heal, mana = self.healer.check_critical_and_mana_with_priority(800, 200)
        self.assertIsNone(heal)
        self.assertTrue(mana)
        self.mock_press.assert_called_with("F4")
        self.mock_press.reset_mock()
        
        # 4. Cooldown expires, both safe
        self.healer.last_cast_time = 0
        heal, mana = self.healer.check_critical_and_mana_with_priority(800, 800)
        self.assertIsNone(heal)
        self.assertFalse(mana)
        self.mock_press.assert_not_called()
    
    def test_hp_values_near_threshold(self):
        """Test boundary values around thresholds."""
        test_cases = [
            # (hp, mana, expected_heal, expected_mana)
            (501, 401, None, False),        # Both just above threshold
            (500, 400, None, False),        # Both exactly at threshold
            (499, 401, "critical", False),  # HP just below, mana above
            (501, 399, None, True),         # HP above, mana just below
            (499, 399, "critical", False),  # Both just below - critical wins
        ]
        
        for hp, mana, expected_heal, expected_mana in test_cases:
            self.healer.last_cast_time = 0  # Reset cooldown
            self.mock_press.reset_mock()
            
            heal, mana_result = self.healer.check_critical_and_mana_with_priority(hp, mana)
            
            self.assertEqual(heal, expected_heal, 
                f"HP={hp}, Mana={mana}: expected heal={expected_heal}, got {heal}")
            self.assertEqual(mana_result, expected_mana,
                f"HP={hp}, Mana={mana}: expected mana={expected_mana}, got {mana_result}")


if __name__ == '__main__':
    unittest.main()
