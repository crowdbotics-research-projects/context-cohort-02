# src/app/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import users, magazines, plans, subscriptions
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    Base.metadata.create_all(bind=engine)


app = FastAPI(lifespan=lifespan)

app.include_router(users.router)
app.include_router(magazines.router)
app.include_router(plans.router)
app.include_router(subscriptions.router)
