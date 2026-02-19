"Tests for fraud scoring service."
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scorer.app import app
from scorer.rules import RuleEngine, check_fraud_rules


client = TestClient(app)


class TestHealthEndpoint:
    "Tests for /health endpoint."
    
    def test_health_returns_200(self):
        response = client.get(/health)
        assert response.status_code == 200
    
    def test_health_returns_status(self):
        response = client.get(/health)
        data = response.json()
        assert status in data
        assert data[status] == healthy
    
    def test_health_returns_version(self):
        response = client.get(/health)
        data = response.json()
        assert version in data


class TestRuleEngine:
    "Tests for the rule engine."
    
    def test_high_velocity_triggers(self):
        engine = RuleEngine()
        txn = {velocity_1h: 10}
        flags = engine.evaluate(txn)
        assert any(HIGH_VELOCITY in f for f in flags)
    
    def test_low_velocity_no_trigger(self):
        engine = RuleEngine()
        txn = {velocity_1h: 1, hour: 14, amount: 50, is_new_device: False}
        flags = engine.evaluate(txn)
        assert not any(HIGH_VELOCITY in f for f in flags)
    
    def test_new_device_triggers(self):
        engine = RuleEngine()
        txn = {is_new_device: True}
        flags = engine.evaluate(txn)
        assert any(NEW_DEVICE in f for f in flags)
    
    def test_unusual_hour_triggers(self):
        engine = RuleEngine()
        txn = {hour: 3}
        flags = engine.evaluate(txn)
        assert any(UNUSUAL_HOUR in f for f in flags)
    
    def test_high_amount_triggers(self):
        engine = RuleEngine()
        txn = {amount: 1000}
        flags = engine.evaluate(txn)
        assert any(HIGH_AMOUNT in f for f in flags)
    
    def test_multiple_rules_can_trigger(self):
        engine = RuleEngine()
        txn = {
            velocity_1h: 10,
            is_new_device: True,
            hour: 3,
            amount: 1000
        }
        flags = engine.evaluate(txn)
        assert len(flags) >= 4
    
    def test_convenience_function(self):
        txn = {is_new_device: True, hour: 2}
        flags = check_fraud_rules(txn)
        assert len(flags) >= 2


class TestScoreEndpoint:
    "Tests for /score endpoint."
    
    @pytest.fixture
    def valid_transaction(self):
        return {
            transaction_id: txn_test_001,
            user_id: user_123,
            amount: 50.0,
            hour: 14,
            day_of_week: 2,
            velocity_1h: 1,
            is_new_device: False
        }
    
    def test_score_requires_model(self, valid_transaction):
        response = client.post(/score, json=valid_transaction)
        assert response.status_code in [200, 503]
    
    def test_score_validates_input(self):
        invalid_txn = {transaction_id: test}
        response = client.post(/score, json=invalid_txn)
        assert response.status_code == 422
    
    def test_score_rejects_negative_amount(self, valid_transaction):
        valid_transaction[amount] = -100
        response = client.post(/score, json=valid_transaction)
        assert response.status_code == 422
    
    def test_score_rejects_invalid_hour(self, valid_transaction):
        valid_transaction[hour] = 25
        response = client.post(/score, json=valid_transaction)
        assert response.status_code == 422


class TestIntegration:
    "Integration tests."
    
    def test_api_workflow(self):
        health_response = client.get(/health)
        assert health_response.status_code == 200
        
        txn = {
            transaction_id: txn_integration_001,
            user_id: user_1,
            amount: 100.0,
            hour: 12,
            day_of_week: 1,
            velocity_1h: 2,
            is_new_device: False
        }
        score_response = client.post(/score, json=txn)
        assert score_response.status_code in [200, 503]


if __name__ == __main__:
    pytest.main([__file__, -v])
EOF