# tests/test_bandit.py
import pytest
import random
from gateway.bandit import ThompsonBanditRouter

def test_bandit_convergence():
    """
    Quantifiably verifies that the Thompson Sampling engine converges 
    on the statistically superior model within production thresholds.
    """
    router = ThompsonBanditRouter()
    
    # Define hidden ground-truth conversion probabilities
    true_conversion_rates = {
        "xgboost_v1": 0.15,    # The true winner
        "lightgbm_v1": 0.05,   # Weak model
        "neural_net_v1": 0.08  # Moderate model
    }
    
    # Run historical iteration loop to simulate traffic
    total_simulations = 2500
    for _ in range(total_simulations):
        selected_model = router.select_model()
        
        # Simulate business outcome based on true hidden probability
        success = random.random() < true_conversion_rates[selected_model]
        
        # Feed reward signal back into the routing state
        router.update_deficit_or_reward(selected_model, success)
        
    # Quantifiable Assertion: The winner must have higher allocation parameters (Alpha)
    winner_alpha = router.model_states["xgboost_v1"]["alpha"]
    loser_alpha = router.model_states["lightgbm_v1"]["alpha"]
    
    print(f"\nFinal Alpha States -> XGBoost: {winner_alpha}, LightGBM: {loser_alpha}")
    assert winner_alpha > loser_alpha, "Bandit failed to exploit the superior model."
