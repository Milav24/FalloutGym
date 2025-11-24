from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.models import User, Membership, MembershipType, Client, MembershipStatus
from app.schemas.memberships import (
    MembershipTypeResponse, MembershipResponse, MembershipCreate,
    MembershipPauseRequest, MembershipHistoryResponse
)

router = APIRouter()


@router.get("/types", response_model=List[MembershipTypeResponse])
def get_membership_types(db: Session = Depends(get_db)):
    """Получить все типы абонементов"""
    types = db.query(MembershipType).filter(MembershipType.is_active == True).all()
    return types


@router.post("/purchase", response_model=MembershipResponse)
def purchase_membership(
        membership_data: MembershipCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """Покупка абонемента"""
    membership_type = db.query(MembershipType).filter(
        MembershipType.id == membership_data.membership_type_id
    ).first()

    if not membership_type:
        raise HTTPException(status_code=404, detail="Тип абонемента не найден")

    client = db.query(Client).filter(Client.user_id == current_user.id).first()

    # Расчет дат
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=membership_type.duration_days)

    # Расчет цены с учетом кастомизации
    total_price = membership_type.price
    if membership_data.custom_options.personal_training:
        total_price += 50
    if membership_data.custom_options.pool_access:
        total_price += 30
    if membership_data.custom_options.spa_access:
        total_price += 40
    if membership_data.custom_options.freezing_allowed:
        total_price += 20

    membership = Membership(
        user_id=current_user.id,
        client_id=client.id,
        membership_type_id=membership_type.id,
        start_date=start_date,
        end_date=end_date,
        custom_options=membership_data.custom_options.dict(),
        status=MembershipStatus.ACTIVE
    )

    db.add(membership)
    db.commit()
    db.refresh(membership)

    return membership


@router.post("/{membership_id}/pause", response_model=MembershipResponse)
def pause_membership(
        membership_id: int,
        pause_data: MembershipPauseRequest,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """Приостановка абонемента"""
    membership = db.query(Membership).filter(
        Membership.id == membership_id,
        Membership.user_id == current_user.id
    ).first()

    if not membership:
        raise HTTPException(status_code=404, detail="Абонемент не найден")

    if membership.status != MembershipStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Абонемент не активен")

    if not membership.custom_options.get('freezing_allowed', False):
        raise HTTPException(status_code=400, detail="Данный абонемент не поддерживает приостановку")

    # Создаем запись о приостановке
    pause_start = datetime.utcnow()
    pause_end = pause_start + timedelta(days=pause_data.pause_days)

    pause_record = {
        "pause_start": pause_start.isoformat(),
        "pause_end": pause_end.isoformat(),
        "reason": pause_data.reason,
        "days": pause_data.pause_days
    }

    membership.current_pause = pause_record
    membership.status = MembershipStatus.PAUSED
    membership.pause_history.append(pause_record)

    db.commit()
    db.refresh(membership)

    return membership


@router.post("/{membership_id}/resume", response_model=MembershipResponse)
def resume_membership(
        membership_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """Возобновление абонемента"""
    membership = db.query(Membership).filter(
        Membership.id == membership_id,
        Membership.user_id == current_user.id
    ).first()

    if not membership:
        raise HTTPException(status_code=404, detail="Абонемент не найден")

    if membership.status != MembershipStatus.PAUSED:
        raise HTTPException(status_code=400, detail="Абонемент не приостановлен")

    if not membership.current_pause:
        raise HTTPException(status_code=400, detail="Нет активной приостановки")

    # Продлеваем абонемент на количество дней приостановки
    pause_days = membership.current_pause.get('days', 0)
    membership.end_date += timedelta(days=pause_days)

    # Обновляем историю
    current_pause = membership.pause_history[-1]
    current_pause['resumed_at'] = datetime.utcnow().isoformat()

    membership.current_pause = None
    membership.status = MembershipStatus.ACTIVE

    db.commit()
    db.refresh(membership)

    return membership


@router.get("/my-memberships", response_model=List[MembershipResponse])
def get_my_memberships(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """Получить мои абонементы"""
    memberships = db.query(Membership).filter(
        Membership.user_id == current_user.id
    ).all()

    return memberships


@router.get("/history", response_model=List[MembershipHistoryResponse])
def get_membership_history(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_active_user)
):
    """Получить историю абонементов"""
    memberships = db.query(Membership).filter(
        Membership.user_id == current_user.id
    ).order_by(Membership.created_at.desc()).all()

    history = []
    for membership in memberships:
        history.append(MembershipHistoryResponse(
            membership=membership,
            purchase_date=membership.created_at,
            total_price=membership.membership_type.price,
            status_changes=membership.pause_history
        ))

    return history