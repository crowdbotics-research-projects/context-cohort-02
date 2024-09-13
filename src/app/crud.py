# src/app/crud.py

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import User, Magazine, Plan, Subscription
from app.schemas.user import UserCreate
from app.schemas.magazine import MagazineCreate, MagazineUpdate
from app.schemas.plan import PlanCreate, PlanUpdate
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate
from app.core.security import verify_password, get_password_hash
from app.core.jwt import create_access_token
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user: UserCreate):
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def deactivate_user(db: Session, username: str):
    user = get_user_by_username(db, username)
    if user:
        user.is_active = False
        db.commit()
        db.refresh(user)
    return user


def reset_password(db: Session, email: str, new_password: str):
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        db.refresh(user)
    return user


def refresh_token(db: Session, username: str):
    from app.core.jwt import create_access_token

    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(days=7)
    )
    return {"access_token": access_token, "refresh_token": refresh_token}


def create_magazine(db: Session, magazine: MagazineCreate):
    db_magazine = Magazine(
        name=magazine.name,
        description=magazine.description,
        base_price=magazine.base_price,
    )
    db.add(db_magazine)
    db.commit()
    db.refresh(db_magazine)
    return db_magazine


def get_magazine(db: Session, magazine_id: int):
    return db.query(Magazine).filter(Magazine.id == magazine_id).first()


def get_magazines(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Magazine).offset(skip).limit(limit).all()


def update_magazine(db: Session, magazine: MagazineUpdate, magazine_id: int):
    db_magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    if db_magazine:
        db_magazine.name = magazine.name
        db_magazine.description = magazine.description
        db_magazine.base_price = magazine.base_price
        db.commit()
        db.refresh(db_magazine)
    return db_magazine


def delete_magazine(db: Session, magazine_id: int):
    db_magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()
    if db_magazine:
        db.delete(db_magazine)
        db.commit()
    return db_magazine


def create_plan(db: Session, plan: PlanCreate):
    db_plan = Plan(
        title=plan.title,
        description=plan.description,
        renewal_period=plan.renewal_period,
        tier=plan.tier,
        discount=plan.discount,
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


def get_plan(db: Session, plan_id: int):
    return db.query(Plan).filter(Plan.id == plan_id).first()


def update_plan(db: Session, plan: PlanUpdate, plan_id: int):
    db_plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if db_plan:
        db_plan.title = plan.title
        db_plan.description = plan.description
        db_plan.renewal_period = plan.renewal_period
        db_plan.tier = plan.tier
        db_plan.discount = plan.discount
        db.commit()
        db.refresh(db_plan)
    return db_plan


def delete_plan(db: Session, plan_id: int):
    db_plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if db_plan:
        db.delete(db_plan)
        db.commit()
    return db_plan


def create_subscription(db: Session, subscription: SubscriptionCreate):
    plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
    if not plan:
        raise ValueError("Invalid plan ID")

    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=plan.renewal_period)

    try:
        price = calculate_price(db, subscription.plan_id, subscription.magazine_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    db_subscription = Subscription(
        user_id=subscription.user_id,
        magazine_id=subscription.magazine_id,
        plan_id=subscription.plan_id,
        start_date=start_date,
        end_date=end_date,
        renewal_date=subscription.renewal_date,
        price=calculate_price(db, subscription.plan_id, subscription.magazine_id),
        is_active=True,
    )
    db.add(db_subscription)
    try:
        db.commit()
        db.refresh(db_subscription)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=422, detail="Subscription already exists")
    return db_subscription


def calculate_price(db: Session, plan_id: int, magazine_id: int) -> float:
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    magazine = db.query(Magazine).filter(Magazine.id == magazine_id).first()

    if not plan or not magazine:
        raise ValueError("Invalid plan or magazine ID")

    base_price = magazine.base_price
    discount = plan.discount

    price = base_price * (1 - discount)
    if price <= 0:
        raise ValueError("Price must be greater than zero")
    return price


def get_subscription(db: Session, subscription_id: int):
    return db.query(Subscription).filter(Subscription.id == subscription_id).first()


def get_subscriptions(db: Session):
    return db.query(Subscription).all()


def delete_subscription(db: Session, subscription_id: int, user_id: int):
    subscription = (
        db.query(Subscription).filter(Subscription.id == subscription_id).first()
    )
    if not subscription:
        return None

    if subscription.user_id != user_id:
        raise ValueError("User does not have permission to delete this subscription")

    subscription.is_active = False
    db.commit()
    db.refresh(subscription)
    return subscription


def get_active_subscriptions(db: Session, user_id: int):
    return (
        db.query(Subscription)
        .filter(Subscription.user_id == user_id, Subscription.is_active == True)
        .all()
    )


def get_subscription_by_id(db: Session, subscription_id: int):
    return db.query(Subscription).filter(Subscription.id == subscription_id).first()


def update_subscription(
    db: Session, subscription_id: int, subscription: SubscriptionUpdate
):
    existing_subscription = (
        db.query(Subscription).filter(Subscription.id == subscription_id).first()
    )

    if not existing_subscription:
        return None

    plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
    if not plan:
        raise ValueError("Invalid plan ID")

    try:
        price = calculate_price(db, subscription.plan_id, subscription.magazine_id)
    except ValueError as e:
        raise ValueError("Calculated price must be greater than zero")

    # Deactivate the existing subscription
    existing_subscription.is_active = False
    db.commit()

    # Use provided start_date and end_date if available, otherwise calculate them
    start_date = subscription.start_date or datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    end_date = subscription.end_date or (
        start_date + timedelta(days=plan.renewal_period * 30)
    )  # Assuming 30 days per month

    # Create a new subscription with the new plan and dates
    new_subscription = Subscription(
        user_id=subscription.user_id,
        magazine_id=subscription.magazine_id,
        plan_id=subscription.plan_id,
        start_date=start_date,
        end_date=end_date,
        renewal_date=subscription.renewal_date,
        price=calculate_price(db, subscription.plan_id, subscription.magazine_id),
        is_active=True,
    )

    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)
    return new_subscription


def deactivate_subscription(db: Session, subscription_id: int):
    subscription = (
        db.query(Subscription).filter(Subscription.id == subscription_id).first()
    )
    if subscription:
        subscription.is_active = False
        db.commit()
        db.refresh(subscription)
    return subscription


def get_plans(db: Session):
    return db.query(Plan).all()
