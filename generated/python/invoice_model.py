from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Invoice(Base):
    """Auto-generated SQLAlchemy model for Invoice."""

    __tablename__ = "invoice"
    id: Optional[int] = Column(Integer, primary_key=True, autoincrement=True)
    comanda_id: uuid.UUID = Column(String, ForeignKey('comanda.id'), nullable=False)
    subtotal_cents: Optional[int] = Column(Integer)
    tax_total_cents: Optional[int] = Column(Integer)
    total_cents: Optional[int] = Column(Integer)
    closed_at: Optional[str] = Column(String)
