from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class OrderItem(Base):
    """Auto-generated SQLAlchemy model for OrderItem."""

    __tablename__ = "order_item"
    id: Optional[int] = Column(Integer, primary_key=True, autoincrement=True)
    order_id: int = Column(Integer, ForeignKey('order.id'), nullable=False)
    item_id: int = Column(Integer, ForeignKey('item.id'), nullable=False)
    quantity: int = Column(Integer, nullable=False)
    unit_price_cents: int = Column(Integer, nullable=False)
    discount_percent: Optional[float] = Column(Float)
    tax_percent: Optional[float] = Column(Float)
    total_cents: Optional[int] = Column(Integer)
    notes: Optional[str] = Column(String)
    last_modified: Optional[str] = Column(String)
    dirty: Optional[bool] = Column(Boolean, default=False)
    origin_device: Optional[str] = Column(String)
