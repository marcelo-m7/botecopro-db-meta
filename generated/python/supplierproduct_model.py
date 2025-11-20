from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class SupplierProduct(Base):
    """Auto-generated SQLAlchemy model for SupplierProduct."""

    __tablename__ = "supplier_product"
    product_id: Optional[int] = Column(Integer, ForeignKey('product.id'), primary_key=True)
    supplier_id: Optional[int] = Column(Integer, ForeignKey('supplier.id'), primary_key=True)
    price_cents: Optional[int] = Column(Integer)
    notes: Optional[str] = Column(String)
