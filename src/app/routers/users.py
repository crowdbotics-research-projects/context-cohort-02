from fastapi import APIRouter, Depends, HTTPException, Query, Security
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db.session import get_db
from app.schemas.user import UserCreate, UserRead, UserLogin
from app.core.jwt import create_access_token, decode_refresh_token, get_current_user
from app.core.security import create_access_token, create_refresh_token
from app.db.session import get_db
from app.schemas.token import Token
from app.models import User
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()


@router.post("/users/register", response_model=UserRead)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    from app.crud import create_user as crud_create_user

    db_user = crud_create_user(db=db, user=user)
    if not db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    return db_user


@router.post("/users/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    from app.crud import authenticate_user

    db_user = authenticate_user(db, user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=15)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.username})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/users/reset-password", response_model=UserRead)
def reset_password_endpoint(email: str, db: Session = Depends(get_db)):
    from app.crud import reset_password as crud_reset_password

    user = crud_reset_password(db, email=email, new_password="newpassword")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/users/deactivate/{username}", response_model=UserRead)
def deactivate_user_endpoint(username: str, db: Session = Depends(get_db)):
    from app.crud import deactivate_user as crud_deactivate_user

    user = crud_deactivate_user(db, username=username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/users/token/refresh", response_model=Token)
def refresh_token(
    refresh_token: str = Security(oauth2_scheme), db: Session = Depends(get_db)
):
    try:
        payload = decode_refresh_token(refresh_token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        access_token_expires = timedelta(minutes=15)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(data={"sub": user.username})
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/users/me", response_model=UserRead)
def read_users_me(current_user: UserRead = Depends(get_current_user)):
    return current_user
