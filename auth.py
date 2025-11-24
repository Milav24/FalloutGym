from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.models.models import User, Client
from app.schemas.users import UserCreate, UserResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Проверяем, что указан email или телефон
    if not user_data.email and not user_data.phone:
        raise HTTPException(
            status_code=400,
            detail="Необходимо указать email или телефон"
        )

    # Проверяем существование пользователя
    existing_user = None
    if user_data.email:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
    if not existing_user and user_data.phone:
        existing_user = db.query(User).filter(User.phone == user_data.phone).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким email или телефоном уже существует"
        )

    # Создаем пользователя
    user = User(
        email=user_data.email,
        phone=user_data.phone,
        password_hash=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        date_of_birth=user_data.date_of_birth
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Создаем клиентский профиль
    client = Client(user_id=user.id)
    db.add(client)
    db.commit()

    return user


@router.post("/login")
def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    # Ищем пользователя по email или username (который может быть телефоном)
    user = db.query(User).filter(
        (User.email == form_data.username) | (User.phone == form_data.username)
    ).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }