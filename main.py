from fastapi import FastAPI,Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db() -> Generator[Session,None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="FastAPI CRUD - Tasks")

@app.get("/health")
def health(db: Session = Depends(get_db)):
    return {"ok": True}