# src/app/models.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Boolean,
    Float,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.db.base import Base
from sqlalchemy.ext.declarative import declarative_base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    subscriptions = relationship("Subscription", back_populates="user")


class Magazine(Base):
    __tablename__ = "magazines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    base_price = Column(Float)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    magazine_id = Column(Integer, ForeignKey("magazines.id"))
    plan_id = Column(Integer, ForeignKey("plans.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    renewal_date = Column(DateTime, nullable=False)
    price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="subscriptions")
    magazine = relationship("Magazine")
    plan = relationship("Plan")

    __table_args__ = (
        UniqueConstraint(
            "user_id", "magazine_id", "plan_id", name="_user_magazine_plan_uc"
        ),
    )


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    renewal_period = Column(Integer)
    tier = Column(Integer)
    discount = Column(Float)

    subscriptions = relationship("Subscription", back_populates="plan")
