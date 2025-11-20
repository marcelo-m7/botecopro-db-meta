from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Employee(Base):
    """Auto-generated SQLAlchemy model for Employee."""

    __tablename__ = "employee"
    id: Optional[int] = Column(Integer, primary_key=True, autoincrement=True)
    name: Optional[str] = Column(String)
    role: Optional[str] = Column(String)
    email: Optional[str] = Column(String)
    hourly_rate_cents: Optional[int] = Column(Integer)
