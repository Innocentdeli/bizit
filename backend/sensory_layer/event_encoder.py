from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, UUID4
import uuid

class UnifiedEvent(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    source: str = Field(..., description="Source system: ERP, CRM, API, etc.")
    event_type: str = Field(..., description="Action type: SALE, STOCK_UPDATE, etc.")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: Dict[str, Any] = Field(..., description="Deep data payload")
    priority: int = Field(default=1, ge=1, le=5)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class EventEncoder:
    @staticmethod
    def encode(source: str, event_type: str, data: Dict[str, Any], priority: int = 1) -> UnifiedEvent:
        """
        Transforms raw input into a UnifiedEvent object.
        This ensures all downstream layers (Kernel, Agents) receive consistent data.
        """
        return UnifiedEvent(
            source=source,
            event_type=event_type,
            payload=data,
            priority=priority
        )

    @staticmethod
    def to_json(event: UnifiedEvent) -> str:
        return event.model_dump_json()
