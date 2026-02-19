"""Tests for fraud scoring service."""
import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scorer.features import extract_features, features_to_array, FEATURE_NAMES
from scorer.rules import RulesEngine

class TestFeatureExtraction:
    def test_extract_features_basic(self):
        txn = {"amount": 100.0, "hour": 14, "day_of_week": 2, "velocity_1h": 2, "is_new_device": False}
        features = extract_features(txn)
        assert "amount_log" in features
        assert "hour_sin" in features
        assert features["is_weekend"] == 0
        assert features["is_night"] == 0
    
    def test_extract_features_night(self):
        txn = {"amount": 50, "hour": 3, "day_of_week": 1, "velocity_1h": 0, "is_new_device": False}
        features = extract_features(txn)
        assert features["is_night"] == 1
    
    def test_extract_features_weekend(self):
        txn = {"amount": 50, "hour": 12, "day_of_week": 6, "velocity_1h": 0, "is_new_device": False}
        features = extract_features(txn)
        assert features["is_weekend"] == 1
    
    def test_features_to_array(self):
        txn = {"amount": 100, "hour": 12, "day_of_week": 0, "velocity_1h": 1, "is_new_device": True}
        features = extract_features(txn)
        arr = features_to_array(features)
        assert len(arr) == len(FEATURE_NAMES)

class TestRulesEngine:
    def setup_method(self):
        self.engine = RulesEngine()
    
    def test_high_velocity_rule(self):
        txn = {"velocity_1h": 10, "amount": 100, "hour": 12, "is_new_device": False}
        result = self.engine.evaluate(txn)
        assert result["rules_count"] > 0
        rule_names = [r["rule"] for r in result["rules_triggered"]]
        assert "high_velocity" in rule_names
    
    def test_new_device_high_amount(self):
        txn = {"velocity_1h": 1, "amount": 600, "hour": 12, "is_new_device": True}
        result = self.engine.evaluate(txn)
        rule_names = [r["rule"] for r in result["rules_triggered"]]
        assert "new_device_high_amount" in rule_names
    
    def test_clean_transaction(self):
        txn = {"velocity_1h": 1, "amount": 50, "hour": 14, "is_new_device": False}
        result = self.engine.evaluate(txn)
        assert result["rules_count"] == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
