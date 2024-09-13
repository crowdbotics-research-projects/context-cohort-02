# src/app/routers/plans.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.plan import PlanCreate, PlanRead
from app.crud import get_plans as crud_get_plans

router = APIRouter()


@router.post("/plans/", response_model=PlanRead)
def create_plan(plan: PlanCreate, db: Session = Depends(get_db)):
    from app.crud import create_plan as crud_create_plan

    if plan.renewal_period <= 0:
        raise HTTPException(
            status_code=422, detail="Renewal period must be greater than zero"
        )
    db_plan = crud_create_plan(db=db, plan=plan)
    if not db_plan:
        raise HTTPException(status_code=400, detail="Plan creation failed")
    return db_plan


@router.get("/plans/", response_model=List[PlanRead])
def read_plans(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    plans = crud_get_plans(db=db)
    if not plans:
        raise HTTPException(status_code=404, detail="No plans found")
    return plans


@router.get("/plans/{plan_id}", response_model=PlanRead)
def read_plan(plan_id: int, db: Session = Depends(get_db)):
    from app.crud import get_plan

    db_plan = get_plan(db, plan_id=plan_id)
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return db_plan


@router.put("/plans/{plan_id}", response_model=PlanRead)
def update_plan(plan_id: int, plan: PlanCreate, db: Session = Depends(get_db)):
    from app.crud import update_plan as crud_update_plan

    db_plan = crud_update_plan(db, plan_id=plan_id, plan=plan)
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return db_plan


@router.delete("/plans/{plan_id}", response_model=PlanRead)
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    from app.crud import delete_plan as crud_delete_plan

    db_plan = crud_delete_plan(db, plan_id=plan_id)
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return db_plan
