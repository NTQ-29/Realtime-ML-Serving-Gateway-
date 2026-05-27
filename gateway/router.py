# gateway/router.py
import hashlib
from typing import List, Tuple
from gateway.bandit import ThompsonBanditRouter

class StrategyRouter:
    def __init__(self, bandit_router: ThompsonBanditRouter):
        self.bandit = bandit_router
        # Default fallback routing rules
        self.primary_model = "xgboost_v1"
        self.shadow_models = ["lightgbm_v1", "neural_net_v1"]

    def _deterministic_hash(self, user_id: str, bucket_count: int = 100) -> int:
        """
        Ensures a user always maps to the same bucket for sticky A/B experiences.
        """
        hasher = hashlib.md5(user_id.encode("utf-8"))
        return int(hasher.hexdigest(), 16) % bucket_count

    def route_request(self, strategy: str, user_id: str) -> Tuple[str, List[str]]:
        """
        Determines the routing execution plan.
        Returns: (Target Model ID for user response, List of Shadow Model IDs to evaluate)
        """
        strategy = strategy.lower()

        # 1. Multi-Armed Bandit Routing Strategy
        if strategy == "bandit":
            target_model = self.bandit.select_model()
            return target_model, []

        # 2. Fixed A/B Testing Strategy (Deterministic per user ID)
        elif strategy == "ab_test":
            bucket = self._deterministic_hash(user_id)
            # 80/20 split scenario: 80% to XGBoost, 20% to LightGBM
            if bucket < 80:
                return "xgboost_v1", []
            else:
                return "lightgbm_v1", []

        # 3. Shadow Mode Strategy (Dual-evaluate, serve primary)
        elif strategy == "shadow":
            return self.primary_model, self.shadow_models

        # Fallback to standard primary model execution
        return self.primary_model, []
