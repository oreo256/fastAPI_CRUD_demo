from fastapi import FastAPI,Depends
from sqlalchemy import create_engine, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase, Mapped, mapped_column
from typing import Generator
from datetime import datetime, timezone

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

class Base(DeclarativeBase):
    pass

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )

Base.metadata.create_all(bind=engine)

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