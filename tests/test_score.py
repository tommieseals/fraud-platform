"""Tests for fraud scoring service."""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scorer.app import app
from scorer.rules import RuleEngine, check_fraud_rules


client = TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_returns_status(self):
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


class TestRuleEngine:
    def test_high_velocity_triggers(self):
        engine = RuleEngine()
        txn = {"velocity_1h": 10}
        flags = engine.evaluate(txn)
        assert any("HIGH_VELOCITY" in f for f in flags)
    
    def test_new_device_triggers(self):
        engine = RuleEngine()
        txn = {"is_new_device": True}
        flags = engine.evaluate(txn)
        assert any("NEW_DEVICE" in f for f in flags)
    
    def test_unusual_hour_triggers(self):
        engine = RuleEngine()
        txn = {"hour": 3}
        flags = engine.evaluate(txn)
        assert any("UNUSUAL_HOUR" in f for f in flags)
    
    def test_high_amount_triggers(self):
        engine = RuleEngine()
        txn = {"amount": 1000}
        flags = engine.evaluate(txn)
        assert any("HIGH_AMOUNT" in f for f in flags)


class TestScoreEndpoint:
    def test_score_requires_model(self):
        txn = {
            "transaction_id": "txn_test",
            "user_id": "user_123",
            "amount": 50.0,
            "hour": 14,
            "day_of_week": 2,
            "velocity_1h": 1,
            "is_new_device": False
        }
        response = client.post("/score", json=txn)
        assert response.status_code in [200, 503]
    
    def test_score_validates_input(self):
        invalid_txn = {"transaction_id": "test"}
        response = client.post("/score", json=invalid_txn)
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])