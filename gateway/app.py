# gateway/app.py
import uuid
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from gateway.bandit import ThompsonBanditRouter
from gateway.router import StrategyRouter

app = FastAPI(
    title="Real-Time Adaptive Model Serving Gateway",
    description="Intelligent API routing gateway for multi-model MLOps deployment.",
    version="1.0.0"
)

# Global router states
bandit_engine = ThompsonBanditRouter()
router_engine = StrategyRouter(bandit_router=bandit_engine)

# Pydantic input/output schemas for rigid API validation
class PredictionRequest(BaseModel):
    user_id: str = Field(..., example="usr_99812")
    routing_strategy: str = Field(default="bandit", description="Options: bandit, ab_test, shadow")
    context_features: Optional[Dict[str, Any]] = Field(default_factory=dict)

class PredictionResponse(BaseModel):
    prediction_id: str
    served_by_model: str
    prediction: float
    routing_strategy_used: str

@app.post("/predict", response_model=PredictionResponse)
async def predict(payload: PredictionRequest):
    """
    Ingests inference requests, assembles real-time vectors, and routes across models.
    """
    try:
        # Step 1: Route the traffic based on specified strategy
        target_model, shadow_models = router_engine.route_request(
            strategy=payload.routing_strategy, 
            user_id=payload.user_id
        )
        
        # Step 2: Simulate feature store retrieval (Feast integration comes next!)
        # In a real environment, we call feast_client.get_online_features() here
        mock_feature_vector = {
            "customer_lifetime_value": 1250.50,
            "session_click_count_30s": 8,
            "device_type": "mobile"
        }
        
        # Unique correlation identifier for tracking delayed rewards downstream
        prediction_id = str(uuid.uuid4())
        
        # Step 3: Mock model container inference responses
        # In a production setup, this would be an internal HTTP/gRPC request to isolated model pods
        mock_predictions = {
            "xgboost_v1": 0.84,
            "lightgbm_v1": 0.79,
            "neural_net_v1": 0.82
        }
        
        # Log shadows asynchronously if shadow mode is active
        if shadow_models:
            for sm in shadow_models:
                # Log shadow prediction info to Kafka for offline alignment
                print(f"[SHADOW LOG] Pred ID {prediction_id} evaluated by {sm}: Result {mock_predictions[sm]}")
                
        final_prediction = mock_predictions.get(target_model, 0.50)
        
        return PredictionResponse(
            prediction_id=prediction_id,
            served_by_model=target_model,
            prediction=final_prediction,
            routing_strategy_used=payload.routing_strategy
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference Routing Error: {str(e)}")

@app.post("/reward")
async def register_reward(prediction_id: str, model_id: str, success: bool):
    """
    Asynchronous reward receiver endpoint to simulate webhook/Kafka feedback loops.
    """
    bandit_engine.update_deficit_or_reward(model_id=model_id, success=success)
    return {
        "status": "reward_processed", 
        "updated_model": model_id,
        "new_state": bandit_engine.model_states[model_id]
    }
