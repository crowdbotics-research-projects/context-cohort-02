# src/app/schemas/plan.py

from pydantic import BaseModel


class PlanBase(BaseModel):
    title: str
    description: str
    renewal_period: int
    tier: int
    discount: float


class PlanCreate(PlanBase):
    pass


class PlanUpdate(PlanBase):
    pass


class PlanRead(PlanBase):
    id: int

    class Config:
        from_attributes = True
