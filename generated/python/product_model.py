from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Product(Base):
    """Auto-generated SQLAlchemy model for Product."""

    __tablename__ = "product"
    id: Optional[int] = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String)
    description: Optional[str] = Column(String)
    cost_price_cents: Optional[int] = Column(Integer)
    stock_current: Optional[float] = Column(Float)
    stock_minimum: Optional[float] = Column(Float)
    unit: Optional[str] = Column(String)
    product_type: Optional[str] = Column(String)
    active: Optional[bool] = Column(Boolean, default=True)
    last_modified: Optional[str] = Column(String)
    dirty: Optional[bool] = Column(Boolean, default=False)
    origin_device: Optional[str] = Column(String)
