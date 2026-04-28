"""
Configuración de la aplicación usando Pydantic Settings
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv

# Load .env file explicitly
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


class Settings(BaseSettings):
    """Configuración de la aplicación"""

    # Aplicación
    app_name: str = "SportAcademia"
    app_version: str = "0.1.0"
    debug: bool = False

    # Base de Datos
    database_url: str = "postgresql+asyncpg://localhost/sport_management_db"

    # JWT
    secret_key: str = "change-this-key-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: List[str] = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:3000",
    ]

    # Email (para futuro)
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    # Stripe (para Phase 6)
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""

    class Config:
        case_sensitive = False


# Crear instancia global de settings
settings = Settings()

