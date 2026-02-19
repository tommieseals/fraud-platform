"""Rules engine for fraud detection."""

class RulesEngine:
    """Rule-based fraud detection layer."""
    
    def __init__(self):
        self.rules = [
            ("high_velocity", self._check_high_velocity),
            ("new_device_high_amount", self._check_new_device_high_amount),
            ("extreme_amount", self._check_extreme_amount),
            ("odd_hours_activity", self._check_odd_hours),
        ]
    
    def _check_high_velocity(self, txn):
        velocity = txn.get("velocity_1h", 0)
        if velocity >= 10:
            return True, 0.8
        elif velocity >= 5:
            return True, 0.4
        return False, 0.0
    
    def _check_new_device_high_amount(self, txn):
        is_new = txn.get("is_new_device", False)
        amount = txn.get("amount", 0)
        if is_new and amount > 500:
            return True, 0.6
        elif is_new and amount > 200:
            return True, 0.3
        return False, 0.0
    
    def _check_extreme_amount(self, txn):
        amount = txn.get("amount", 0)
        if amount > 5000:
            return True, 0.7
        elif amount > 2000:
            return True, 0.3
        return False, 0.0
    
    def _check_odd_hours(self, txn):
        hour = txn.get("hour", 12)
        amount = txn.get("amount", 0)
        if hour < 5 and amount > 100:
            return True, 0.4
        return False, 0.0
    
    def evaluate(self, txn):
        triggered = []
        max_score = 0.0
        for rule_name, rule_func in self.rules:
            fired, score = rule_func(txn)
            if fired:
                triggered.append({"rule": rule_name, "score": score})
                max_score = max(max_score, score)
        return {
            "rules_triggered": triggered,
            "rules_score": max_score,
            "rules_count": len(triggered),
        }
