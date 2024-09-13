# src/app/routers/subscriptions.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionRead,
    SubscriptionUpdate,
)
from app.crud import (
    create_subscription,
    get_subscriptions,
    update_subscription,
    delete_subscription,
    get_subscription_by_id,  # Add this import
)
from app.db.session import get_db
from app.core.jwt import get_current_user
from app.schemas.user import UserRead

router = APIRouter()


@router.post("/subscriptions/", response_model=SubscriptionRead)
def create_subscription_endpoint(
    subscription: SubscriptionCreate, db: Session = Depends(get_db)
):
    db_subscription = create_subscription(db=db, subscription=subscription)
    if not db_subscription:
        raise HTTPException(status_code=400, detail="Subscription could not be created")
    return db_subscription


@router.put("/subscriptions/{subscription_id}", response_model=SubscriptionRead)
def update_subscription_endpoint(
    subscription_id: int,
    subscription: SubscriptionUpdate,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
):
    try:
        updated_subscription = update_subscription(db, subscription_id, subscription)
        if not updated_subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return updated_subscription
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/subscriptions/", response_model=list[SubscriptionRead])
def get_subscriptions_endpoint(db: Session = Depends(get_db)):
    subscriptions = get_subscriptions(db=db)
    if not subscriptions:
        raise HTTPException(status_code=404, detail="No subscriptions found")
    return subscriptions


@router.get("/subscriptions/{subscription_id}", response_model=SubscriptionRead)
def get_subscription_endpoint(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
):
    subscription = get_subscription_by_id(db, subscription_id)
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    if subscription.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this subscription"
        )
    return subscription


@router.delete("/subscriptions/{subscription_id}", response_model=SubscriptionRead)
def delete_subscription_endpoint(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_user),
):
    try:
        deleted_subscription = delete_subscription(db, subscription_id, current_user.id)
        if not deleted_subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        return deleted_subscription
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
