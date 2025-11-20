from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class MovementType(Enum):
    IN = "in"
    OUT = "out"
    ADJUSTMENT = "adjustment"


class StockMovement(Base):
    """Auto-generated SQLAlchemy model for StockMovement."""

    __tablename__ = "stock_movement"
    id: Optional[int] = Column(Integer, primary_key=True, autoincrement=True)
    product_id: int = Column(Integer, ForeignKey('product.id'), nullable=False)
    quantity: float = Column(Float, nullable=False)
    movement_type: MovementType = Column(SAEnum(MovementType), nullable=False)
    reason: Optional[str] = Column(String)
    related_order_item: Optional[int] = Column(Integer, ForeignKey('order_item.id'))
    created_at: Optional[str] = Column(String)
