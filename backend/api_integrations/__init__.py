"""
API Integrations Module

This module provides integration clients for external business platforms:
- Shopify (E-commerce)
- Stripe (Payments)
- QuickBooks (Accounting)
- Plaid (Banking)
- Salesforce (CRM)
- SAP (ERP)
"""

from .base_client import BaseAPIClient
from .integration_manager import IntegrationManager

__all__ = [
    "BaseAPIClient",
    "IntegrationManager",
]
