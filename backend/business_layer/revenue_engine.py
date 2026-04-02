class RevenueEngine:
    """
    Implements the Transactional Business Model.
    Calculates fees based on realized value (Outcome-based pricing).
    """
    
    def __init__(self):
        self.total_revenue = 0.0
        self.pending_invoices = []

    def calculate_optimization_fee(self, realized_utility: float, action_type: str) -> float:
        """
        Calculates the 'tax' BIZIT takes for optimizing a decision.
        Model:
        - Cost Savings: 5% of saved amount
        - Revenue Gen: 2% of transaction value
        """
        fee = 0.0
        
        if "SAVE" in action_type or "EFFICIENCY" in action_type:
            # Value is interpreted as savings
            fee = realized_utility * 0.05
        elif "SELL" in action_type or "REVENUE" in action_type:
             # Value is interpreted as revenue
            fee = realized_utility * 0.02
        else:
            # Flat fee for processing generic complex tasks
            fee = 0.10 
            
        self.total_revenue += fee
        self.pending_invoices.append({"action": action_type, "value": realized_utility, "fee": fee})
        
        print(f"[BUSINESS] Revenue Generated: ${fee:.2f} (from Value: ${realized_utility:.2f})")
        return fee

    def get_financial_report(self):
        return {
            "total_revenue": self.total_revenue,
            "invoice_count": len(self.pending_invoices)
        }
