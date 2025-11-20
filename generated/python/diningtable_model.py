from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class DiningTable(Base):
    """Auto-generated SQLAlchemy model for DiningTable."""

    __tablename__ = "dining_table"
    id: Optional[int] = Column(Integer, primary_key=True, autoincrement=True)
    table_num: int = Column(Integer)
    seats: Optional[int] = Column(Integer)
    available: Optional[bool] = Column(Boolean, default=True)
