from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class TicketStatus(Enum):
    NEW = "new"
    COOKING = "cooking"
    READY = "ready"
    DELIVERED = "delivered"


class KitchenTicket(Base):
    """Auto-generated SQLAlchemy model for KitchenTicket."""

    __tablename__ = "kitchen_ticket"
    id: Optional[int] = Column(Integer, primary_key=True, autoincrement=True)
    order_id: int = Column(Integer, ForeignKey('order.id'), nullable=False)
    status: TicketStatus = Column(SAEnum(TicketStatus), nullable=False)
    created_at: Optional[str] = Column(String)
