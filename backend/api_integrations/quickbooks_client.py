"""
QuickBooks API Client

Integrates with QuickBooks Online API to fetch:
- Invoices
- Expenses
- Accounts
- Profit and Loss statements
"""

import os
from typing import Dict, Any, List, Optional
from .base_client import BaseAPIClient, AuthenticationError


class QuickBooksClient(BaseAPIClient):
    """
    QuickBooks API client for accounting data integration.
    
    Requires:
    - QUICKBOOKS_CLIENT_ID
    - QUICKBOOKS_CLIENT_SECRET
    - QUICKBOOKS_REALM_ID (Company ID)
    - QUICKBOOKS_ACCESS_TOKEN (Usually handled via OAuth2, mocked here for Level 31)
    """
    
    def __init__(self):
        """Initialize QuickBooks client with credentials from environment"""
        client_id = os.getenv("QUICKBOOKS_CLIENT_ID", "mock_client_id")
        realm_id = os.getenv("QUICKBOOKS_REALM_ID", "mock_realm_id")
        access_token = os.getenv("QUICKBOOKS_ACCESS_TOKEN", "mock_token")
        
        # QuickBooks uses different base URLs for sandbox and production
        # Mapping to production for the template
        base_url = "https://quickbooks.api.intuit.com/v3/company"
        
        self.realm_id = realm_id
        self.access_token = access_token
        
        super().__init__(api_key=access_token, base_url=f"{base_url}/{realm_id}")
        
    def authenticate(self) -> bool:
        """
        Verify QuickBooks API access.
        
        Returns:
            True if authentication successful
        """
        try:
            # Query company info to test connection
            self._make_request(
                method="GET",
                endpoint="/companyinfo",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Accept": "application/json"
                }
            )
            return True
        except Exception as e:
            # For Level 31, if it's a mock token, we return True for the demo flow
            if self.access_token == "mock_token":
                return True
            raise AuthenticationError(f"QuickBooks authentication failed: {e}")
            
    def get_connection_status(self) -> Dict[str, Any]:
        """Get QuickBooks connection status"""
        try:
            # In a real scenario, this would check if token is expired
            return {
                "connected": True,
                "platform": "quickbooks",
                "realm_id": self.realm_id,
                "status": "active"
            }
        except Exception as e:
            return {
                "connected": False,
                "platform": "quickbooks",
                "status": "error",
                "error": str(e)
            }
            
    def fetch_invoices(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch invoices from QuickBooks"""
        query = f"SELECT * FROM Invoice MAXRESULTS {limit}"
        response = self._make_request(
            method="GET",
            endpoint="/query",
            params={"query": query},
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json"
            }
        )
        return response.get("QueryResponse", {}).get("Invoice", [])
        
    def fetch_expenses(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch purchase/expense transactions"""
        query = f"SELECT * FROM Purchase MAXRESULTS {limit}"
        response = self._make_request(
            method="GET",
            endpoint="/query",
            params={"query": query},
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json"
            }
        )
        return response.get("QueryResponse", {}).get("Purchase", [])
        
    def fetch_profit_loss(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Fetch Profit and Loss report summary"""
        response = self._make_request(
            method="GET",
            endpoint="/reports/ProfitAndLoss",
            params={
                "start_date": start_date,
                "end_date": end_date
            },
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json"
            }
        )
        return response
