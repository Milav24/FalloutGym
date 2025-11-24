import pygame
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Fitness Club API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # База данных
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/fitness_club")

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 дней

    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Yandex Cloud
    YANDEX_ACCESS_KEY: str = os.getenv("YANDEX_ACCESS_KEY")
    YANDEX_SECRET_KEY: str = os.getenv("YANDEX_SECRET_KEY")
    YANDEX_BUCKET_NAME: str = os.getenv("YANDEX_BUCKET_NAME", "fitness-club")
    YANDEX_REGION: str = os.getenv("YANDEX_REGION", "ru-central1")

    # ЮKassa
    YOOKASSA_SHOP_ID: str = os.getenv("YOOKASSA_SHOP_ID")
    YOOKASSA_SECRET_KEY: str = os.getenv("YOOKASSA_SECRET_KEY")

    # SMTP для уведомлений
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "noreply@fitnessclub.com")

    class Config:
        case_sensitive = True


settings = Settings()