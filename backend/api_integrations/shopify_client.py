"""
Shopify API Client

Integrates with Shopify REST Admin API to fetch:
- Products
- Orders
- Customers
- Inventory levels
"""

import os
from typing import Dict, Any, List, Optional
from .base_client import BaseAPIClient, AuthenticationError


class ShopifyClient(BaseAPIClient):
    """
    Shopify API client for e-commerce data integration.
    
    Requires:
        - SHOPIFY_API_KEY
        - SHOPIFY_API_SECRET
        - SHOPIFY_STORE_URL
    """
    
    def __init__(self):
        """Initialize Shopify client with credentials from environment"""
        api_key = os.getenv("SHOPIFY_API_KEY")
        api_secret = os.getenv("SHOPIFY_API_SECRET")
        store_url = os.getenv("SHOPIFY_STORE_URL")
        
        if not all([api_key, api_secret, store_url]):
            raise ValueError("Missing Shopify credentials in environment variables")
        
        self.api_secret = api_secret
        base_url = f"{store_url}/admin/api/2024-01"
        
        super().__init__(api_key=api_key, base_url=base_url)
        
    def authenticate(self) -> bool:
        """
        Verify Shopify API credentials.
        
        Returns:
            True if authentication successful
        """
        try:
            # Test authentication with a simple API call
            self._make_request(
                method="GET",
                endpoint="/shop.json",
                headers={"X-Shopify-Access-Token": self.api_key}
            )
            return True
        except Exception as e:
            raise AuthenticationError(f"Shopify authentication failed: {e}")
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get Shopify connection status"""
        try:
            shop_data = self._make_request(
                method="GET",
                endpoint="/shop.json",
                headers={"X-Shopify-Access-Token": self.api_key}
            )
            return {
                "connected": True,
                "platform": "shopify",
                "store_name": shop_data.get("shop", {}).get("name"),
                "status": "active"
            }
        except Exception as e:
            return {
                "connected": False,
                "platform": "shopify",
                "status": "error",
                "error": str(e)
            }
    
    def fetch_products(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch products from Shopify.
        
        Args:
            limit: Maximum number of products to fetch
            
        Returns:
            List of product dictionaries
        """
        response = self._make_request(
            method="GET",
            endpoint="/products.json",
            params={"limit": limit},
            headers={"X-Shopify-Access-Token": self.api_key}
        )
        return response.get("products", [])
    
    def fetch_orders(self, limit: int = 50, status: str = "any") -> List[Dict[str, Any]]:
        """
        Fetch orders from Shopify.
        
        Args:
            limit: Maximum number of orders to fetch
            status: Order status filter (any, open, closed, cancelled)
            
        Returns:
            List of order dictionaries
        """
        response = self._make_request(
            method="GET",
            endpoint="/orders.json",
            params={"limit": limit, "status": status},
            headers={"X-Shopify-Access-Token": self.api_key}
        )
        return response.get("orders", [])
    
    def fetch_customers(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch customers from Shopify.
        
        Args:
            limit: Maximum number of customers to fetch
            
        Returns:
            List of customer dictionaries
        """
        response = self._make_request(
            method="GET",
            endpoint="/customers.json",
            params={"limit": limit},
            headers={"X-Shopify-Access-Token": self.api_key}
        )
        return response.get("customers", [])
    
    def fetch_inventory(self) -> List[Dict[str, Any]]:
        """
        Fetch inventory levels from Shopify.
        
        Returns:
            List of inventory level dictionaries
        """
        response = self._make_request(
            method="GET",
            endpoint="/inventory_levels.json",
            headers={"X-Shopify-Access-Token": self.api_key}
        )
        return response.get("inventory_levels", [])
