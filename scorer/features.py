"""Feature extraction for fraud detection."""
import numpy as np

def extract_features(transaction):
    """Extract ML features from a transaction."""
    amount = float(transaction.get("amount", 0))
    hour = int(transaction.get("hour", 12))
    day_of_week = int(transaction.get("day_of_week", 0))
    velocity_1h = int(transaction.get("velocity_1h", 0))
    is_new_device = int(transaction.get("is_new_device", False))
    features = {
        "amount_log": np.log1p(amount),
        "amount_scaled": min(amount / 1000, 10),
        "hour_sin": np.sin(2 * np.pi * hour / 24),
        "hour_cos": np.cos(2 * np.pi * hour / 24),
        "is_night": 1 if hour < 6 or hour > 22 else 0,
        "is_weekend": 1 if day_of_week >= 5 else 0,
        "velocity_1h": velocity_1h,
        "velocity_high": 1 if velocity_1h > 5 else 0,
        "is_new_device": is_new_device,
        "amount_velocity_interaction": np.log1p(amount) * velocity_1h,
    }
    return features

FEATURE_NAMES = [
    "amount_log", "amount_scaled", "hour_sin", "hour_cos",
    "is_night", "is_weekend", "velocity_1h", "velocity_high",
    "is_new_device", "amount_velocity_interaction"
]

def features_to_array(features):
    """Convert feature dict to array for model input."""
    return np.array([features[f] for f in FEATURE_NAMES])
