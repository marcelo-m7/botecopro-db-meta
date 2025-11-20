from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class PaymentSplit(Base):
    """Auto-generated SQLAlchemy model for PaymentSplit."""

    __tablename__ = "payment_split"
    id: Optional[int] = Column(Integer, primary_key=True, autoincrement=True)
    payment_id: int = Column(Integer, ForeignKey('payment.id'), nullable=False)
    payee_name: Optional[str] = Column(String)
    amount_cents: int = Column(Integer, nullable=False)
