"""Operational metrics for fraud scoring service."""
from dataclasses import dataclass, field
from typing import Dict
from collections import deque
import threading

@dataclass
class MetricsCollector:
    window_size: int = 1000
    _latencies: deque = field(default_factory=lambda: deque(maxlen=1000))
    _decisions: Dict[str, int] = field(default_factory=lambda: {"APPROVE": 0, "REVIEW": 0, "DECLINE": 0})
    _scores: deque = field(default_factory=lambda: deque(maxlen=1000))
    _request_count: int = 0
    _error_count: int = 0
    _lock: threading.Lock = field(default_factory=threading.Lock)
    
    def record_request(self, latency_ms, decision, fraud_score):
        with self._lock:
            self._latencies.append(latency_ms)
            self._decisions[decision] = self._decisions.get(decision, 0) + 1
            self._scores.append(fraud_score)
            self._request_count += 1
    
    def record_error(self):
        with self._lock:
            self._error_count += 1
    
    def get_metrics(self):
        with self._lock:
            latencies = list(self._latencies)
            if latencies:
                latency_stats = {
                    "p50": sorted(latencies)[len(latencies) // 2],
                    "p95": sorted(latencies)[int(len(latencies) * 0.95)],
                    "mean": sum(latencies) / len(latencies),
                }
            else:
                latency_stats = {"p50": 0, "p95": 0, "mean": 0}
            return {
                "request_count": self._request_count,
                "error_count": self._error_count,
                "latency_ms": latency_stats,
                "decisions": self._decisions.copy(),
            }

metrics = MetricsCollector()
