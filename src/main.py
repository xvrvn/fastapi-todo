from fastapi import FastAPI

from src.auth.router import router as auth_router

from .database import init_db

app = FastAPI(title="Todo API", version="0.1.0")

init_db()

app.include_router(auth_router, prefix="/auth", tags=["auth"])


@app.get("/")
def root():
    return {"message": "Welcome to Todo API"}
