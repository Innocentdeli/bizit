from typing import List, Dict, Any
import statistics

class Oracle:
    """
    Level 10: The Oracle (Predictive Prophet).
    Uses past Blockchain history to predict future state.
    """
    def __init__(self, blockchain):
        self.blockchain = blockchain

    def predict_metabolic_stress(self, horizon_ticks: int = 10) -> float:
        """
        Predicts the Weisman Score in N ticks using Linear Regression.
        """
        history = []
        # Extract utility values from blocks (simplified)
        for block in self.blockchain.chain[-50:]: # Last 50 blocks
            if "action" in block.data:
                 # Mock extracting a numeric value from string actions
                 val = 0.8 # baseline
                 if "OPTIMIZE" in block.data["action"]: val = 0.9
                 if "EXPAND" in block.data["action"]: val = 0.7
                 history.append(val)
        
        if len(history) < 5:
            return 0.5 # Not enough data
            
        # Simple Linear Regression (y = mx + b)
        x = list(range(len(history)))
        y = history
        
        n = len(x)
        m_x = statistics.mean(x)
        m_y = statistics.mean(y)
        
        numerator = sum((xi - m_x) * (yi - m_y) for xi, yi in zip(x, y))
        denominator = sum((xi - m_x) ** 2 for xi in x)
        
        if denominator == 0: slope = 0
        else: slope = numerator / denominator
        
        intercept = m_y - slope * m_x
        
        # Predict future
        future_x = n + horizon_ticks
        prediction = slope * future_x + intercept
        
        return max(0.0, min(1.0, prediction))

    def consult(self):
        pred = self.predict_metabolic_stress()
        print(f"🔮 [ORACLE] Predicting System Health in 10 ticks: {pred:.2f}")
        return pred
