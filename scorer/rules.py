"""Rule engine for fraud detection."""


class RuleEngine:
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
    
    def evaluate(self, transaction):
        flags = []
        for rule in self.rules:
            result = rule(transaction)
            if result:
                flags.append(result)
        return flags
    
    def _check_high_velocity(self, txn):
        if txn.get("velocity_1h", 0) >= self.VELOCITY_1H_THRESHOLD:
            return "HIGH_VELOCITY_1H:" + str(txn.get("velocity_1h"))
        return None
    
    def _check_new_device(self, txn):
        if txn.get("is_new_device", False):
            return "NEW_DEVICE"
        return None
    
    def _check_unusual_hour(self, txn):
        hour = txn.get("hour", 12)
        if hour in self.UNUSUAL_HOURS:
            return "UNUSUAL_HOUR:" + str(hour)
        return None
    
    def _check_high_amount(self, txn):
        amount = txn.get("amount", 0)
        if amount >= self.HIGH_AMOUNT_THRESHOLD:
            return "HIGH_AMOUNT:$" + str(round(amount, 2))
        return None


def check_fraud_rules(transaction):
    engine = RuleEngine()
    return engine.evaluate(transaction)