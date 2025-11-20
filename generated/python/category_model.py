from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Category(Base):
    """Auto-generated SQLAlchemy model for Category."""

    __tablename__ = "category"
    id: Optional[int] = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String)
