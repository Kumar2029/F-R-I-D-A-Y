from Backend.StrategyHealth import StrategyHealthManager
import unittest
import os
import shutil

class TestStrategyCooldown(unittest.TestCase):
    def setUp(self):
        # Use a temporary memory dir or just ensure we don't break prod?
        # StrategyHealthManager uses "memory/strategy_health.json" directly.
        # I should back it up.
        self.health_file = "memory/strategy_health.json"
        self.backup_file = "memory/strategy_health.json.bak"
        if os.path.exists(self.health_file):
            shutil.copy(self.health_file, self.backup_file)
            
        self.mgr = StrategyHealthManager()
        # Reset health for test strategy
        if "test_strat" in self.mgr.health_map:
            del self.mgr.health_map["test_strat"]

    def tearDown(self):
        # Restore backup
        if os.path.exists(self.backup_file):
            shutil.move(self.backup_file, self.health_file)

    def test_cooldown_logic(self):
        strat = "test_strat"
        
        # Seed logic: 2 Successes
        self.mgr.record_success(strat)
        self.mgr.record_success(strat)
        
        # 1. First Failure
        self.mgr.record_failure(strat)
        health = self.mgr.get_health(strat)
        self.assertEqual(health.consecutive_failures, 1)
        self.assertEqual(health.cooldown_remaining, 0)
        self.assertGreater(health.score, 0.0)
        
        # 2. Second Failure -> Freeze
        self.mgr.record_failure(strat)
        health = self.mgr.get_health(strat)
        self.assertEqual(health.consecutive_failures, 2)
        self.assertEqual(health.cooldown_remaining, 3)
        self.assertEqual(health.score, 0.0) # Should be 0 when cooling down
        
        print("Cooldown activation verified.")
        
        # 3. Success Resets
        self.mgr.record_success(strat)
        health = self.mgr.get_health(strat)
        self.assertEqual(health.consecutive_failures, 0)
        self.assertEqual(health.cooldown_remaining, 0)
        self.assertGreater(health.score, 0.0)
        
        print("Cooldown reset verified.")

if __name__ == '__main__':
    unittest.main()
