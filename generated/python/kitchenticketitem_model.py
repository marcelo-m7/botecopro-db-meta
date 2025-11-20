from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class KitchenTicketItem(Base):
    """Auto-generated SQLAlchemy model for KitchenTicketItem."""

    __tablename__ = "kitchen_ticket_item"
    id: Optional[int] = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id: int = Column(Integer, ForeignKey('kitchen_ticket.id'), nullable=False)
    order_item_id: int = Column(Integer, ForeignKey('order_item.id'), nullable=False)
