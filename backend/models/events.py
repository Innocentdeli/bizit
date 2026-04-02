from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, Optional

class BizEvent(BaseModel):
    id: Optional[str] = None
    source: str = Field(..., description="Source of the event (e.g., 'ERP', 'CRM', 'API')")
    event_type: str = Field(..., description="Type of business event (e.g., 'SALE', 'INVENTORY_LOW', 'MARKET_SHIFT')")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(..., description="Specific payload for the event")
    priority: int = Field(default=1, ge=0, le=5, description="Priority level (0-5)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context or tracing info")

    class Config:
        json_schema_extra = {
            "example": {
                "source": "SHOPIFY",
                "event_type": "ORDER_CREATED",
                "data": {"order_id": "12345", "amount": 250.00, "currency": "USD"},
                "priority": 2
            }
        }
