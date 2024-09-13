# src/app/schemas/subscription.py

from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional


class SubscriptionBase(BaseModel):
    user_id: int
    magazine_id: int
    plan_id: int
    start_date: date
    end_date: date
    renewal_date: date
    is_active: bool = True


class SubscriptionCreate(SubscriptionBase):
    user_id: int
    magazine_id: int
    plan_id: int
    renewal_date: date
    start_date: Optional[datetime] = None  # Now optional
    end_date: Optional[datetime] = None  # Now optional


class SubscriptionUpdate(BaseModel):
    user_id: int
    magazine_id: int
    plan_id: int
    renewal_date: datetime
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: bool = True


class SubscriptionRead(SubscriptionBase):
    id: int
    price: float
    is_active: bool

    class Config:
        from_attributes = True
