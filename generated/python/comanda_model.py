from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ComandaStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class Comanda(Base):
    """Auto-generated SQLAlchemy model for Comanda."""

    __tablename__ = "comanda"
    id: Optional[uuid.UUID] = Column(String, primary_key=True)
    table_id: Optional[int] = Column(Integer, ForeignKey('dining_table.id'))
    status: ComandaStatus = Column(SAEnum(ComandaStatus), nullable=False)
    opened_at: Optional[str] = Column(String)
    closed_at: Optional[str] = Column(String)
    subtotal_cents: Optional[int] = Column(Integer)
    total_cents: Optional[int] = Column(Integer)
    notes: Optional[str] = Column(String)
    last_modified: Optional[str] = Column(String)
    dirty: Optional[bool] = Column(Boolean, default=False)
    origin_device: Optional[str] = Column(String)
