"Rule engine for fraud detection."
from typing import Any


class RuleEngine:
    " Fraud detection rule engine. Evaluates transactions against business rules. "
    
    VELOCITY_1H_THRESHOLD = 5
    HIGH_AMOUNT_THRESHOLD = 500
    UNUSUAL_HOURS = {0, 1, 2, 3, 4, 5}
    
    def __init__(self):
        self.rules = [
            self._check_high_velocity,
            self._check_new_device,
            self._check_unusual_hour,
            self._check_high_amount,
        ]
    
    def evaluate(self, transaction: dict) -> list:
        "Evaluate all rules against a transaction."
        flags = []
        for rule in self.rules:
            result = rule(transaction)
            if result:
                flags.append(result)
        return flags
    
    def _check_high_velocity(self, txn: dict):
        "Flag high transaction velocity."
        if txn.get(velocity_1h, 0) >= self.VELOCITY_1H_THRESHOLD:
            return fHIGH_VELOCITY_1H:txn.get(velocity_1h)
        return None
    
    def _check_new_device(self, txn: dict):
        "Flag transactions from new devices."
        if txn.get(is_new_device, False):
            return NEW_DEVICE
        return None
    
    def _check_unusual_hour(self, txn: dict):
        "Flag transactions at unusual hours."
        hour = txn.get(hour, 12)
        if hour in self.UNUSUAL_HOURS:
            return fUNUSUAL_HOUR:hour
        return None
    
    def _check_high_amount(self, txn: dict):
        "Flag high-value transactions."
        amount = txn.get(amount, 0)
        if amount >= self.HIGH_AMOUNT_THRESHOLD:
            return fHIGH_AMOUNT:$amount:.2f
        return None


def check_fraud_rules(transaction: dict) -> list:
    "Check transaction against all fraud rules."
    engine = RuleEngine()
    return engine.evaluate(transaction)
EOF