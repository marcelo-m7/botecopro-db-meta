from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ItemProduct(Base):
    """Auto-generated SQLAlchemy model for ItemProduct."""

    __tablename__ = "item_product"
    item_id: Optional[int] = Column(Integer, ForeignKey('item.id'), primary_key=True)
    product_id: Optional[int] = Column(Integer, ForeignKey('product.id'), primary_key=True)
    quantity: float = Column(Float, nullable=False)
