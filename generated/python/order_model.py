from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class OrderStatus(Enum):
    OPEN = "open"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OriginType(Enum):
    TABLE = "table"
    TAKEAWAY = "takeaway"
    DELIVERY = "delivery"


class Order(Base):
    """Auto-generated SQLAlchemy model for Order."""

    __tablename__ = "order"
    id: Optional[int] = Column(Integer, primary_key=True, autoincrement=True)
    comanda_id: uuid.UUID = Column(String, ForeignKey('comanda.id'), nullable=False)
    employee_id: Optional[int] = Column(Integer, ForeignKey('employee.id'))
    customer_id: Optional[int] = Column(Integer, ForeignKey('customer.id'))
    origin: OriginType = Column(SAEnum(OriginType), nullable=False)
    status: OrderStatus = Column(SAEnum(OrderStatus), nullable=False)
    created_at: Optional[str] = Column(String)
    notes: Optional[str] = Column(String)
    last_modified: Optional[str] = Column(String)
    dirty: Optional[bool] = Column(Boolean, default=False)
    origin_device: Optional[str] = Column(String)
