import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta

class TrendPredictor:
    """Predicts appetite and energy trends using synthetic 7-day dataset"""
    
    def __init__(self):
        # Generate synthetic 7-day historical data
        self.synthetic_data = self._generate_synthetic_data()
    
    def _generate_synthetic_data(self) -> List[Dict]:
        """Generate 7 days of synthetic wellness data"""
        np.random.seed(42)
        days = []
        base_date = datetime.now() - timedelta(days=7)
        
        for i in range(7):
            days.append({
                "date": (base_date + timedelta(days=i)).isoformat(),
                "appetite": np.random.choice(["low", "normal", "high"], p=[0.2, 0.6, 0.2]),
                "energy": np.random.choice(["low", "medium"], p=[0.3, 0.7]),
                "mood": np.random.choice(["happy", "neutral", "low", "stressed", "tired"], 
                                        p=[0.3, 0.4, 0.1, 0.1, 0.1]),
                "adherence": np.random.randint(60, 95)
            })
        return days
    
    def predict_trends(self, current_context: Dict) -> Dict[str, str]:
        """Predict appetite and energy trends"""
        # Simple trend analysis from synthetic data
        recent_appetites = [d["appetite"] for d in self.synthetic_data[-3:]]
        recent_energies = [d["energy"] for d in self.synthetic_data[-3:]]
        
        # Count occurrences
        appetite_counts = {"low": 0, "normal": 0, "high": 0}
        energy_counts = {"low": 0, "medium": 0}
        
        for a in recent_appetites:
            appetite_counts[a] = appetite_counts.get(a, 0) + 1
        for e in recent_energies:
            energy_counts[e] = energy_counts.get(e, 0) + 1
        
        # Predict based on trend
        predicted_appetite = max(appetite_counts, key=appetite_counts.get)
        predicted_energy = max(energy_counts, key=energy_counts.get)
        
        # Adjust based on current mood
        if current_context.get("mood") in ["low", "stressed", "tired"]:
            if predicted_appetite == "high":
                predicted_appetite = "normal"
            predicted_energy = "low"
        
        return {
            "appetite_trend": predicted_appetite,
            "energy_trend": predicted_energy,
            "confidence": 0.7  # Synthetic data confidence
        }

