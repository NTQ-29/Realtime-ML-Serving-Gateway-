# gateway/bandit.py
import random
import math

class ThompsonBanditRouter:
    def __init__(self):
        # Alpha=Successes, Beta=Failures. Initialized to uniform distribution (1.0)
        self.model_states = {
            "xgboost_v1": {"alpha": 1.0, "beta": 1.0},
            "lightgbm_v1": {"alpha": 1.0, "beta": 1.0},
            "neural_net_v1": {"alpha": 1.0, "beta": 1.0}
        }

    def pseudo_beta_sample(self, alpha: float, beta: float) -> float:
        """Samples from a Beta(alpha, beta) distribution using Gamma relationships."""
        def sample_gamma(shape):
            if shape < 1.0:
                return sample_gamma(shape + 1.0) * (random.random() ** (1.0 / shape))
            d = shape - 1.0 / 3.0
            c = 1.0 / math.sqrt(9.0 * d)
            while True:
                x = random.gauss(0, 1)
                v = 1.0 + c * x
                if v <= 0: continue
                v = v * v * v
                u = random.random()
                if u < 1.0 - 0.0331 * x * x * x * x: return d * v
                if math.log(u) < 0.5 * x * x + d * (1.0 - v + math.log(v)): return d * v

        gamma_a = sample_gamma(alpha)
        gamma_b = sample_gamma(beta)
        return gamma_a / (gamma_a + gamma_b) if (gamma_a + gamma_b) > 0 else 0.0

    def select_model(self) -> str:
        best_model = None
        highest_sample = -1.0
        for model_id, params in self.model_states.items():
            sample = self.pseudo_beta_sample(params["alpha"], params["beta"])
            if sample > highest_sample:
                highest_sample = sample
                best_model = model_id
        return best_model

    def update_deficit_or_reward(self, model_id: str, success: bool):
        if model_id in self.model_states:
            if success:
                self.model_states[model_id]["alpha"] += 1.0
            else:
                self.model_states[model_id]["beta"] += 1.0
