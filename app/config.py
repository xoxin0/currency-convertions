"""Конфигурация приложения. Все настройки вынесены в отдельный файл для удобства."""

import os
from pathlib import Path

# Корень проекта (папка, где лежит этот файл)
BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Класс с настройками приложения"""

    # База данных
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/currencies.db")
    # Сервер
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    # API
    API_PREFIX = "/api/v1"  # Будет префикс для всех маршрутов


# Создаём экземпляр для импорта в других модулях
config = Config()
