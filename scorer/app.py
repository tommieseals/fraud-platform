"""FastAPI fraud scoring service."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import numpy as np
from pathlib import Path
import time

from scorer.rules import RuleEngine

app = FastAPI(
    title="Fraud Scoring API",
    description="Real-time fraud detection scoring service",
    version="1.0.0"
)

MODEL_PATH = Path(__file__).parent.parent / "models" / "fraud_model.joblib"
model = None
rule_engine = RuleEngine()


class Transaction(BaseModel):
    transaction_id: str
    user_id: str
    amount: float = Field(ge=0)
    hour: int = Field(ge=0, le=23)
    day_of_week: int = Field(ge=0, le=6)
    velocity_1h: int = Field(ge=0)
    is_new_device: bool = False


class ScoringResponse(BaseModel):
    transaction_id: str
    fraud_score: float
    rule_flags: list
    final_decision: str
    latency_ms: float


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str


@app.on_event("startup")
async def load_model():
    global model
    if MODEL_PATH.exists():
        model = joblib.load(MODEL_PATH)
        print("Model loaded from " + str(MODEL_PATH))
    else:
        print("Warning: Model not found at " + str(MODEL_PATH))


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        model_loaded=model is not None,
        version="1.0.0"
    )


@app.post("/score", response_model=ScoringResponse)
async def score_transaction(txn: Transaction):
    start_time = time.time()
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    features = np.array([[
        txn.amount,
        txn.hour,
        txn.day_of_week,
        txn.velocity_1h,
        int(txn.is_new_device)
    ]])
    
    fraud_prob = float(model.predict_proba(features)[0][1])
    
    rule_flags = rule_engine.evaluate(txn.dict())
    
    if fraud_prob > 0.8 or len(rule_flags) >= 3:
        decision = "DECLINE"
    elif fraud_prob > 0.5 or len(rule_flags) >= 1:
        decision = "REVIEW"
    else:
        decision = "APPROVE"
    
    latency_ms = (time.time() - start_time) * 1000
    
    return ScoringResponse(
        transaction_id=txn.transaction_id,
        fraud_score=round(fraud_prob, 4),
        rule_flags=rule_flags,
        final_decision=decision,
        latency_ms=round(latency_ms, 2)
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)