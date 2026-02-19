"FastAPI fraud scoring service."
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import numpy as np
from pathlib import Path
import time

from scorer.rules import RuleEngine

app = FastAPI(
    title=Fraud Scoring API,
    description=Real-time fraud detection scoring service,
    version=1.0.0
)

MODEL_PATH = Path(__file__).parent.parent / models / fraud_model.joblib
model = None
rule_engine = RuleEngine()


class Transaction(BaseModel):
    "Transaction input schema."
    transaction_id: str = Field(..., description=Unique transaction ID)
    user_id: str = Field(..., description=User identifier)
    amount: float = Field(..., ge=0, description=Transaction amount in USD)
    hour: int = Field(..., ge=0, le=23, description=Hour of transaction (0-23))
    day_of_week: int = Field(..., ge=0, le=6, description=Day of week (0=Monday))
    velocity_1h: int = Field(..., ge=0, description=Transactions in last hour)
    is_new_device: bool = Field(default=False, description=Is this a new device)


class ScoringResponse(BaseModel):
    "Scoring response schema."
    transaction_id: str
    fraud_score: float = Field(..., ge=0, le=1)
    rule_flags: list = Field(default_factory=list)
    final_decision: str
    latency_ms: float


class HealthResponse(BaseModel):
    "Health check response."
    status: str
    model_loaded: bool
    version: str


@app.on_event(startup)
async def load_model():
    "Load the ML model on startup."
    global model
    if MODEL_PATH.exists():
        model = joblib.load(MODEL_PATH)
        print(fModel loaded from MODEL_PATH)
    else:
        print(fWarning: Model not found at MODEL_PATH)


@app.get(/health, response_model=HealthResponse)
async def health_check():
    "Health check endpoint."
    return HealthResponse(
        status=healthy,
        model_loaded=model is not None,
        version=1.0.0
    )


@app.post(/score, response_model=ScoringResponse)
async def score_transaction(txn: Transaction):
    "Score a transaction for fraud risk."
    start_time = time.time()
    
    if model is None:
        raise HTTPException(status_code=503, detail=Model not loaded)
    
    features = np.array([[
        txn.amount,
        txn.hour,
        txn.day_of_week,
        txn.velocity_1h,
        int(txn.is_new_device)
    ]])
    
    fraud_prob = float(model.predict_proba(features)[0][1])
    
    rule_flags = rule_engine.evaluate(txn.model_dump())
    
    if fraud_prob > 0.8 or len(rule_flags) >= 3:
        decision = DECLINE
    elif fraud_prob > 0.5 or len(rule_flags) >= 1:
        decision = REVIEW
    else:
        decision = APPROVE
    
    latency_ms = (time.time() - start_time) * 1000
    
    return ScoringResponse(
        transaction_id=txn.transaction_id,
        fraud_score=round(fraud_prob, 4),
        rule_flags=rule_flags,
        final_decision=decision,
        latency_ms=round(latency_ms, 2)
    )


if __name__ == __main__:
    import uvicorn
    uvicorn.run(app, host=0.0.0.0, port=8000)
EOF