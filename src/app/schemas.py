# src/app/schemas.py

from datetime import date
from pydantic import BaseModel
from typing import List, Optional


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    is_active: bool
    subscriptions: List[int] = []

    class Config:
        from_attributes = True


class MagazineBase(BaseModel):
    name: str
    description: Optional[str] = None
    base_price: float


class MagazineCreate(MagazineBase):
    pass


class MagazineRead(MagazineBase):
    id: int

    class Config:
        from_attributes = True


class PlanBase(BaseModel):
    title: str
    description: Optional[str] = None
    renewal_period: int
    discount: float


class PlanCreate(PlanBase):
    pass


class PlanRead(PlanBase):
    id: int

    class Config:
        from_attributes = True


class SubscriptionBase(BaseModel):
    user_id: int
    magazine_id: int
    plan_id: int
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class SubscriptionCreate(BaseModel):
    user_id: int
    magazine_id: int
    plan_id: int
    renewal_date: date
    start_date: date
    end_date: date


class SubscriptionRead(SubscriptionBase):
    id: int

    class Config:
        from_attributes = True
