"""FastAPI fraud scoring service."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scorer.features import extract_features, features_to_array
from scorer.rules import RulesEngine
from scorer.model_loader import get_model_loader

app = FastAPI(title="Fraud Scoring API", version="1.0.0")
rules_engine = RulesEngine()

class Transaction(BaseModel):
    transaction_id: str
    user_id: str
    merchant_id: str
    device_id: str
    amount: float
    hour: int
    day_of_week: int
    velocity_1h: int
    is_new_device: bool

class ScoreResponse(BaseModel):
    transaction_id: str
    fraud_score: float
    ml_score: float
    rules_score: float
    decision: str
    rules_triggered: List[Dict[str, Any]]
    latency_ms: float

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str

@app.get("/health", response_model=HealthResponse)
async def health():
    try:
        get_model_loader().load()
        model_loaded = True
    except Exception:
        model_loaded = False
    return HealthResponse(status="healthy", model_loaded=model_loaded, version="1.0.0")

@app.post("/score", response_model=ScoreResponse)
async def score(transaction: Transaction):
    start = time.time()
    txn_dict = transaction.model_dump()
    try:
        features = extract_features(txn_dict)
        feature_array = features_to_array(features)
        ml_score = get_model_loader().predict_proba(feature_array)
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Model not loaded")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    rules_result = rules_engine.evaluate(txn_dict)
    rules_score = rules_result["rules_score"]
    fraud_score = 0.7 * ml_score + 0.3 * rules_score
    if fraud_score >= 0.7:
        decision = "DECLINE"
    elif fraud_score >= 0.4:
        decision = "REVIEW"
    else:
        decision = "APPROVE"
    latency_ms = (time.time() - start) * 1000
    return ScoreResponse(
        transaction_id=transaction.transaction_id,
        fraud_score=round(fraud_score, 4),
        ml_score=round(ml_score, 4),
        rules_score=round(rules_score, 4),
        decision=decision,
        rules_triggered=rules_result["rules_triggered"],
        latency_ms=round(latency_ms, 2)
    )
