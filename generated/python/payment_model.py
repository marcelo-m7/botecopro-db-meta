from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class PaymentMethod(Enum):
    CASH = "cash"
    CARD = "card"
    PIX = "pix"
    VOUCHER = "voucher"
    TAB = "tab"


class Payment(Base):
    """Auto-generated SQLAlchemy model for Payment."""

    __tablename__ = "payment"
    id: Optional[int] = Column(Integer, primary_key=True, autoincrement=True)
    comanda_id: uuid.UUID = Column(String, ForeignKey('comanda.id'), nullable=False)
    method: PaymentMethod = Column(SAEnum(PaymentMethod), nullable=False)
    amount_cents: int = Column(Integer, nullable=False)
    received_at: Optional[str] = Column(String)
    notes: Optional[str] = Column(String)
