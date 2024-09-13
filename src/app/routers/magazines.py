# src/app/routers/magazines.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import Magazine
from app.schemas.magazine import MagazineCreate, MagazineUpdate, MagazineRead
from app.crud import get_magazines as crud_get_magazines

router = APIRouter()


@router.post("/magazines/", response_model=MagazineRead)
def create_magazine(magazine: MagazineCreate, db: Session = Depends(get_db)):
    from app.crud import create_magazine as crud_create_magazine

    return crud_create_magazine(db=db, magazine=magazine)


@router.get("/magazines/", response_model=List[MagazineRead])
def read_magazines(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    magazines = crud_get_magazines(db=db, skip=skip, limit=limit)
    if not magazines:
        raise HTTPException(status_code=404, detail="No magazines found")
    return magazines


@router.get("/magazines/{magazine_id}", response_model=MagazineRead)
def read_magazine(magazine_id: int, db: Session = Depends(get_db)):
    from app.crud import get_magazine

    db_magazine = get_magazine(db, magazine_id=magazine_id)
    if not db_magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    return db_magazine


@router.put("/magazines/{magazine_id}", response_model=MagazineRead)
def update_magazine(
    magazine_id: int, magazine: MagazineUpdate, db: Session = Depends(get_db)
):
    from app.crud import update_magazine as crud_update_magazine

    db_magazine = crud_update_magazine(db, magazine_id=magazine_id, magazine=magazine)
    if not db_magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    return db_magazine


@router.delete("/magazines/{magazine_id}", response_model=MagazineRead)
def delete_magazine(magazine_id: int, db: Session = Depends(get_db)):
    from app.crud import delete_magazine as crud_delete_magazine

    db_magazine = crud_delete_magazine(db, magazine_id=magazine_id)
    if not db_magazine:
        raise HTTPException(status_code=404, detail="Magazine not found")
    return db_magazine
