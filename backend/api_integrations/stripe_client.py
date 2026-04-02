"""
Stripe API Client

Integrates with Stripe API to fetch:
- Payments
- Subscriptions
- Invoices
- Customers
"""

import os
from typing import Dict, Any, List, Optional
from .base_client import BaseAPIClient, AuthenticationError


class StripeClient(BaseAPIClient):
    """
    Stripe API client for payment data integration.
    
    Requires:
        - STRIPE_API_KEY
    """
    
    def __init__(self):
        """Initialize Stripe client with credentials from environment"""
        api_key = os.getenv("STRIPE_API_KEY")
        
        if not api_key:
            raise ValueError("Missing STRIPE_API_KEY in environment variables")
        
        super().__init__(api_key=api_key, base_url="https://api.stripe.com/v1")
        
    def authenticate(self) -> bool:
        """
        Verify Stripe API credentials.
        
        Returns:
            True if authentication successful
        """
        try:
            # Test authentication with account retrieval
            self._make_request(
                method="GET",
                endpoint="/account",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return True
        except Exception as e:
            raise AuthenticationError(f"Stripe authentication failed: {e}")
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get Stripe connection status"""
        try:
            account_data = self._make_request(
                method="GET",
                endpoint="/account",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return {
                "connected": True,
                "platform": "stripe",
                "account_id": account_data.get("id"),
                "business_name": account_data.get("business_profile", {}).get("name"),
                "status": "active"
            }
        except Exception as e:
            return {
                "connected": False,
                "platform": "stripe",
                "status": "error",
                "error": str(e)
            }
    
    def fetch_payments(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch payment intents from Stripe.
        
        Args:
            limit: Maximum number of payments to fetch
            
        Returns:
            List of payment intent dictionaries
        """
        response = self._make_request(
            method="GET",
            endpoint="/payment_intents",
            params={"limit": limit},
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.get("data", [])
    
    def fetch_subscriptions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch subscriptions from Stripe.
        
        Args:
            limit: Maximum number of subscriptions to fetch
            
        Returns:
            List of subscription dictionaries
        """
        response = self._make_request(
            method="GET",
            endpoint="/subscriptions",
            params={"limit": limit},
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.get("data", [])
    
    def fetch_invoices(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch invoices from Stripe.
        
        Args:
            limit: Maximum number of invoices to fetch
            
        Returns:
            List of invoice dictionaries
        """
        response = self._make_request(
            method="GET",
            endpoint="/invoices",
            params={"limit": limit},
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.get("data", [])
    
    def fetch_customers(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch customers from Stripe.
        
        Args:
            limit: Maximum number of customers to fetch
            
        Returns:
            List of customer dictionaries
        """
        response = self._make_request(
            method="GET",
            endpoint="/customers",
            params={"limit": limit},
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.get("data", [])
