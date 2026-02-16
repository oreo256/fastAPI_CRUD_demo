from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy import create_engine, String, Boolean, DateTime, select
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase, Mapped, mapped_column
from typing import Generator, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

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
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title="FastAPI CRUD - Tasks")


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    completed: Optional[bool] = None


class TaskOut(BaseModel):
    id: int
    title: str
    completed: bool
    created_at: datetime

    class Config:
        from_attributes = True


@app.get("/health")
def health(db: Session = Depends(get_db)):
    return {"ok": True}


@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = Task(title=payload.title)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@app.get("/tasks", response_model=List[TaskOut])
def list_tasks(
    db: Session = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    # これは古い書き方。通るけど、新しく勉強するならstmtの方が良い
    # tasks = db.query(Task).order_by(Task.id.desc()).offset(offset).limit(limit).all()
    # stmtはstatementの略
    stmt = (select(Task).order_by(Task.id.desc()).offset(offset).limit(limit))
    tasks = db.execute(stmt).scalar().all()
    return tasks

@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task