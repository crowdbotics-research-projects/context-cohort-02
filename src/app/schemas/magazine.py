# src/app/schemas/magazine.py

from pydantic import BaseModel


class MagazineBase(BaseModel):
    name: str
    description: str
    base_price: float


class MagazineCreate(MagazineBase):
    pass


class MagazineUpdate(MagazineBase):
    pass


class MagazineRead(MagazineBase):
    id: int

    class Config:
        from_attributes = True
