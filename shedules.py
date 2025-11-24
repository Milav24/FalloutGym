from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.models import Training, Trainer, User
from app.schemas.schedules import TrainingResponse, TrainingCreate

router = APIRouter()


@router.get("/", response_model=List[TrainingResponse])
def get_trainings(
        skip: int = 0,
        limit: int = 100,
        trainer_id: Optional[int] = Query(None),
        training_type: Optional[str] = Query(None),
        date_from: Optional[date] = Query(None),
        date_to: Optional[date] = Query(None),
        status: Optional[str] = Query(None),
        db: Session = Depends(get_db)
):
    """Получить расписание тренировок"""
    query = db.query(Training)

    if trainer_id:
        query = query.filter(Training.trainer_id == trainer_id)

    if training_type:
        query = query.filter(Training.type == training_type)

    if date_from:
        query = query.filter(Training.start_time >= date_from)

    if date_to:
        query = query.filter(Training.start_time <= date_to)

    if status:
        query = query.filter(Training.status == status)

    # Показываем только будущие тренировки
    query = query.filter(Training.start_time >= datetime.utcnow())

    trainings = query.offset(skip).limit(limit).order_by(Training.start_time).all()
    return trainings


@router.get("/available", response_model=List[TrainingResponse])
def get_available_trainings(
        skip: int = 0,
        limit: int = 50,
        trainer_id: Optional[int] = Query(None),
        training_type: Optional[str] = Query(None),
        db: Session = Depends(get_db)
):
    """Получить доступные для записи тренировки"""
    query = db.query(Training).filter(
        Training.status == "available",
        Training.start_time >= datetime.utcnow()
    )

    if trainer_id:
        query = query.filter(Training.trainer_id == trainer_id)

    if training_type:
        query = query.filter(Training.type == training_type)

    trainings = query.offset(skip).limit(limit).order_by(Training.start_time).all()
    return trainings


@router.get("/week")
def get_week_schedule(
        week_offset: int = Query(0, description="Смещение недели (0 - текущая)"),
        db: Session = Depends(get_db)
):
    """Получить расписание на неделю"""
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    end_date = start_date + timedelta(days=6)

    trainings = db.query(Training).filter(
        Training.start_time >= start_date,
        Training.start_time <= end_date
    ).order_by(Training.start_time).all()

    # Группируем по дням
    schedule = {}
    for training in trainings:
        day = training.start_time.date()
        if day not in schedule:
            schedule[day] = []
        schedule[day].append(TrainingResponse.from_orm(training))

    return schedule