from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.models import Trainer, User, Review
from app.schemas.trainers import TrainerResponse, TrainerCreate, ReviewResponse

router = APIRouter()


@router.get("/", response_model=List[TrainerResponse])
def get_trainers(
        skip: int = 0,
        limit: int = 100,
        specialization: str = None,
        db: Session = Depends(get_db)
):
    """Получить список тренеров"""
    query = db.query(Trainer).filter(Trainer.is_active == True)

    if specialization:
        query = query.filter(Trainer.specialization.contains(specialization))

    trainers = query.offset(skip).limit(limit).all()
    return trainers


@router.get("/{trainer_id}", response_model=TrainerResponse)
def get_trainer(trainer_id: int, db: Session = Depends(get_db)):
    """Получить информацию о тренере"""
    trainer = db.query(Trainer).filter(Trainer.id == trainer_id).first()
    if not trainer:
        raise HTTPException(status_code=404, detail="Тренер не найден")

    return trainer


@router.get("/{trainer_id}/reviews", response_model=List[ReviewResponse])
def get_trainer_reviews(
        trainer_id: int,
        skip: int = 0,
        limit: int = 50,
        db: Session = Depends(get_db)
):
    """Получить отзывы о тренере"""
    trainer = db.query(Trainer).filter(Trainer.id == trainer_id).first()
    if not trainer:
        raise HTTPException(status_code=404, detail="Тренер не найден")

    reviews = db.query(Review).filter(
        Review.trainer_id == trainer_id
    ).offset(skip).limit(limit).order_by(Review.created_at.desc()).all()

    return reviews