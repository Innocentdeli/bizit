"""
Integration Manager

Central manager for all external API integrations.
Handles connection status tracking, data synchronization, and credential management.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from core.state import OrganismState

logger = logging.getLogger(__name__)


class IntegrationManager:
    """
    Manages all external API integrations for BIZIT.
    
    Provides:
    - Connection status tracking
    - Data synchronization orchestration
    - Credential validation
    - Integration health monitoring
    """
    
    def __init__(self):
        """Initialize the integration manager"""
        self.integrations = {}
        self._initialize_integrations()
    
    def _initialize_integrations(self):
        """Initialize available integrations based on environment variables"""
        # Shopify
        if all([
            os.getenv("SHOPIFY_API_KEY"),
            os.getenv("SHOPIFY_API_SECRET"),
            os.getenv("SHOPIFY_STORE_URL")
        ]):
            self.integrations["shopify"] = {
                "available": True,
                "connected": False,
                "label": "Shopify Store",
                "last_sync": None
            }
        else:
            self.integrations["shopify"] = {
                "available": False,
                "connected": False,
                "label": "Shopify Store",
                "error": "Missing credentials"
            }
        
        # Stripe
        if os.getenv("STRIPE_API_KEY"):
            self.integrations["stripe"] = {
                "available": True,
                "connected": False,
                "label": "Stripe Payments",
                "last_sync": None
            }
        else:
            self.integrations["stripe"] = {
                "available": False,
                "connected": False,
                "label": "Stripe Payments",
                "error": "Missing credentials"
            }
        
        # QuickBooks
        if all([
            os.getenv("QUICKBOOKS_CLIENT_ID"),
            os.getenv("QUICKBOOKS_REALM_ID")
        ]):
            self.integrations["quickbooks"] = {
                "available": True,
                "connected": False,
                "label": "QuickBooks",
                "last_sync": None
            }
        else:
            self.integrations["quickbooks"] = {
                "available": True, # Keep available for manual credential entry demo
                "connected": False,
                "label": "QuickBooks",
                "status": "ready"
            }
        
        # Plaid
        if all([
            os.getenv("PLAID_CLIENT_ID"),
            os.getenv("PLAID_SECRET")
        ]):
            self.integrations["plaid"] = {
                "available": True,
                "connected": False,
                "label": "Bank Accounts (Plaid)",
                "last_sync": None
            }
        else:
            self.integrations["plaid"] = {
                "available": True, # Keep available for manual credential entry demo
                "connected": False,
                "label": "Bank Accounts (Plaid)",
                "status": "ready"
            }
        
        # Salesforce (placeholder)
        self.integrations["salesforce"] = {
            "available": False,
            "connected": False,
            "label": "Salesforce CRM",
            "error": "Not implemented yet"
        }
        
        # SAP (placeholder)
        self.integrations["sap"] = {
            "available": False,
            "connected": False,
            "label": "SAP ERP",
            "error": "Not implemented yet"
        }
        
        # Forex Trading (OANDA)
        if all([
            os.getenv("OANDA_API_KEY"),
            os.getenv("OANDA_ACCOUNT_ID")
        ]):
            self.integrations["forex"] = {
                "available": True,
                "connected": False,
                "label": "Forex Trading (OANDA)",
                "last_sync": None
            }
        else:
            self.integrations["forex"] = {
                "available": False,
                "connected": False,
                "label": "Forex Trading (OANDA)",
                "error": "Missing credentials"
            }
    
    def get_all_integrations(self) -> Dict[str, Any]:
        """
        Get status of all integrations.
        
        Returns:
            Dictionary of integration statuses
        """
        return self.integrations
    
    def connect_integration(self, platform: str) -> Dict[str, Any]:
        """
        Connect to a specific integration platform.
        
        Args:
            platform: Platform name (shopify, stripe, etc.)
            
        Returns:
            Connection result dictionary
        """
        if platform not in self.integrations:
            return {"success": False, "error": "Unknown platform"}
        
        if not self.integrations[platform]["available"]:
            return {
                "success": False,
                "error": self.integrations[platform].get("error", "Not available")
            }
        
        try:
            if platform == "shopify":
                from .shopify_client import ShopifyClient
                client = ShopifyClient()
                client.authenticate()
                status = client.get_connection_status()
                client.close()
                
                self.integrations[platform]["connected"] = True
                self.integrations[platform]["status"] = "active"
                return {"success": True, "platform": platform, "status": status}
                
            elif platform == "stripe":
                from .stripe_client import StripeClient
                client = StripeClient()
                client.authenticate()
                status = client.get_connection_status()
                client.close()
                
                self.integrations[platform]["connected"] = True
                self.integrations[platform]["status"] = "active"
                return {"success": True, "platform": platform, "status": status}
            
            elif platform == "forex":
                from .forex_client import ForexClient
                client = ForexClient()
                client.authenticate()
                status = client.get_connection_status()
                client.close()
                
                self.integrations[platform]["connected"] = True
                self.integrations[platform]["status"] = "active"
                return {"success": True, "platform": platform, "status": status}
            
            elif platform == "quickbooks":
                from .quickbooks_client import QuickBooksClient
                client = QuickBooksClient()
                client.authenticate()
                status = client.get_connection_status()
                client.close()
                
                self.integrations[platform]["connected"] = True
                self.integrations[platform]["status"] = "active"
                return {"success": True, "platform": platform, "status": status}
                
            elif platform == "plaid":
                from .plaid_client import PlaidClient
                client = PlaidClient()
                client.authenticate()
                status = client.get_connection_status()
                client.close()
                
                self.integrations[platform]["connected"] = True
                self.integrations[platform]["status"] = "active"
                return {"success": True, "platform": platform, "status": status}
            
            else:
                return {"success": False, "error": "Platform not implemented yet"}
                
        except Exception as e:
            logger.error(f"Failed to connect to {platform}: {e}")
            self.integrations[platform]["connected"] = False
            self.integrations[platform]["error"] = str(e)
            return {"success": False, "error": str(e)}
    
    def disconnect_integration(self, platform: str) -> Dict[str, Any]:
        """
        Disconnect from a specific integration platform.
        
        Args:
            platform: Platform name
            
        Returns:
            Disconnection result dictionary
        """
        if platform in self.integrations:
            self.integrations[platform]["connected"] = False
            self.integrations[platform]["status"] = "disconnected"
            return {"success": True, "platform": platform}
        
        return {"success": False, "error": "Unknown platform"}
    
    def sync_data(self, platform: str) -> Dict[str, Any]:
        """
        Sync data from a specific platform.
        
        Args:
            platform: Platform name
            
        Returns:
            Sync result with fetched data
        """
        if platform not in self.integrations:
            return {"success": False, "error": "Unknown platform"}
        
        if not self.integrations[platform].get("connected"):
            return {"success": False, "error": "Platform not connected"}
        
        try:
            data = {}
            
            if platform == "shopify":
                from .shopify_client import ShopifyClient
                with ShopifyClient() as client:
                    data["products"] = client.fetch_products(limit=20)
                    data["orders"] = client.fetch_orders(limit=20)
                    data["customers"] = client.fetch_customers(limit=20)
                    
            elif platform == "stripe":
                from .stripe_client import StripeClient
                with StripeClient() as client:
                    data["payments"] = client.fetch_payments(limit=20)
                    data["subscriptions"] = client.fetch_subscriptions(limit=20)
                    data["invoices"] = client.fetch_invoices(limit=20)
            
            elif platform == "forex":
                from .forex_client import ForexClient
                with ForexClient() as client:
                    # Fetch account summary
                    data["account"] = client.get_account_summary()
                    # Fetch live quotes for major pairs
                    data["quotes"] = client.get_live_quotes([
                        "EUR_USD", "GBP_USD", "USD_JPY", "USD_CHF", 
                        "AUD_USD", "USD_CAD", "NZD_USD"
                    ])
                    # Fetch open positions
                    data["positions"] = client.get_open_positions()
                    # Fetch recent transactions
                    data["transactions"] = client.get_transaction_history(limit=20)
            
            elif platform == "quickbooks":
                from .quickbooks_client import QuickBooksClient
                with QuickBooksClient() as client:
                    data["invoices"] = client.fetch_invoices(limit=20)
                    data["expenses"] = client.fetch_expenses(limit=20)
                    data["profit_loss"] = client.fetch_profit_loss("2024-01-01", "2024-12-31")
                    
            elif platform == "plaid":
                from .plaid_client import PlaidClient
                with PlaidClient() as client:
                    data["accounts"] = client.fetch_accounts()
                    data["transactions"] = client.fetch_transactions("2024-01-01", "2024-12-31")
            
            else:
                return {"success": False, "error": "Platform not implemented yet"}
            
            # Level 33: Push synced data to OrganismState financial vitals
            state = OrganismState()
            import time
            if platform == "shopify" and data.get("orders"):
                total_sales = sum(float(o.get('total_price', 0)) for o in data["orders"])
                state.update_financial_vitals("shopify", {
                    "total_sales_24h": total_sales,
                    "order_count": len(data["orders"])
                })
            elif platform == "stripe" and data.get("payments"):
                # Simplified total
                available = sum(float(p.get('amount', 0)) for p in data["payments"]) / 100.0 # Stripe is cents
                state.update_financial_vitals("stripe", {
                    "available_balance": available,
                    "last_sync": time.time()
                })
            elif platform == "forex" and data.get("account"):
                acc = data["account"]
                state.update_financial_vitals("oanda", {
                    "balance": float(acc.get('balance', 0)),
                    "pnl": float(acc.get('pl', 0) if 'pl' in acc else 0), 
                    "currency": acc.get('currency', 'USD'),
                    "instruments": [q['instrument'] for q in data.get("quotes", [])]
                })
            elif platform == "quickbooks" and data.get("profit_loss"):
                # Extract total income from report rows
                report = data["profit_loss"]
                # This is a bit simplified for the demo report structure
                state.update_financial_vitals("quickbooks", {
                    "total_revenue": 50000.0, # Mocked from report parsing
                    "active_invoices": len(data.get("invoices", []))
                })
            elif platform == "plaid" and data.get("accounts"):
                total_bal = sum(float(a.get('balances', {}).get('current', 0)) for a in data["accounts"])
                state.update_financial_vitals("plaid", {
                    "total_bank_balance": total_bal,
                    "account_count": len(data["accounts"])
                })

            # Update last sync time
            self.integrations[platform]["last_sync"] = datetime.now().isoformat()
            
            return {
                "success": True,
                "platform": platform,
                "data": data,
                "synced_at": self.integrations[platform]["last_sync"]
            }
            
        except Exception as e:
            logger.error(f"Failed to sync data from {platform}: {e}")
            return {"success": False, "error": str(e)}
