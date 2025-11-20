from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ItemType(Enum):
    DISH = "dish"
    DRINK = "drink"
    ARTICLE = "article"


class Item(Base):
    """Auto-generated SQLAlchemy model for Item."""

    __tablename__ = "item"
    id: Optional[int] = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String)
    description: Optional[str] = Column(String)
    sale_price_cents: Optional[int] = Column(Integer)
    unit_cost_cents: Optional[int] = Column(Integer)
    prep_time_min: Optional[int] = Column(Integer)
    item_type: ItemType = Column(SAEnum(ItemType), nullable=False)
    category_id: Optional[int] = Column(Integer, ForeignKey('category.id'))
    subcategory_id: Optional[int] = Column(Integer, ForeignKey('subcategory.id'))
    active: Optional[bool] = Column(Boolean, default=True)
    notes: Optional[str] = Column(String)
    last_modified: Optional[str] = Column(String)
    dirty: Optional[bool] = Column(Boolean, default=False)
    origin_device: Optional[str] = Column(String)
