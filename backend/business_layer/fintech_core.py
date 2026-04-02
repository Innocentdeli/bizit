class FinTechCore:
    """
    Mock implementation of the Embedded Finance Layer.
    Controls the flow of money, lending, and payments.
    """
    
    def __init__(self):
        self.balance = 100000.00 # Initial capital
        self.credit_line = 50000.00
    
    def process_payment(self, amount: float, recipient: str):
        print(f"[FINTECH] Processing payment of ${amount} to {recipient}...")
        self.balance -= amount
        return {"status": "success", "tx_id": "PAY-12345"}
    
    def request_working_capital(self, amount: float):
        """
        Factoring/Lending logic.
        """
        if amount < self.credit_line:
            self.balance += amount
            self.credit_line -= amount
            print(f"[FINTECH] Capital Loan Approved: +${amount}")
            return True
        else:
            print(f"[FINTECH] Loan Denied: Exceeds credit limit.")
            return False

    def get_status(self):
        return {"cash_balance": self.balance, "available_credit": self.credit_line}
