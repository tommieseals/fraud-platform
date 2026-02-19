"""PSI-based drift detection for fraud model."""
import numpy as np

def calculate_psi(expected, actual, bins=10):
    """Calculate Population Stability Index."""
    breakpoints = np.percentile(expected, np.linspace(0, 100, bins + 1))
    breakpoints[0] = -np.inf
    breakpoints[-1] = np.inf
    expected_counts = np.histogram(expected, bins=breakpoints)[0]
    actual_counts = np.histogram(actual, bins=breakpoints)[0]
    expected_pct = (expected_counts + 0.001) / (len(expected) + 0.001 * bins)
    actual_pct = (actual_counts + 0.001) / (len(actual) + 0.001 * bins)
    psi = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
    return psi

def interpret_psi(psi):
    if psi < 0.1:
        return "NO_DRIFT"
    elif psi < 0.2:
        return "SLIGHT_DRIFT"
    else:
        return "SIGNIFICANT_DRIFT"

class DriftMonitor:
    def __init__(self, reference_data, feature_columns):
        self.reference = reference_data
        self.feature_columns = feature_columns
        
    def check_drift(self, current_data):
        results = {"features": {}, "overall_status": "NO_DRIFT", "max_psi": 0.0}
        for col in self.feature_columns:
            if col in self.reference.columns and col in current_data.columns:
                psi = calculate_psi(self.reference[col].values, current_data[col].values)
                results["features"][col] = {"psi": round(psi, 4), "status": interpret_psi(psi)}
                results["max_psi"] = max(results["max_psi"], psi)
        if results["max_psi"] >= 0.2:
            results["overall_status"] = "SIGNIFICANT_DRIFT"
        elif results["max_psi"] >= 0.1:
            results["overall_status"] = "SLIGHT_DRIFT"
        return results
