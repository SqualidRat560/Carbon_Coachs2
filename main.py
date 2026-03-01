from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routes import router
from db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Carbon Coach API", version="0.1.0", lifespan=lifespan)
app.include_router(router)


@app.get("/")
def root():
    return {"status": "Carbon Coach API is running"}
