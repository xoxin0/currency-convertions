"""Настройка подключения к базе данных. Используется SQLAlchemy ORM для работы с SQLite."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import config

# Создаём движок (engine) — низкоуровневое подключение к БД
# connect_args={"check_same_thread": False} нужно только для SQLite,
# чтобы несколько потоков могли работать с одной БД (для разработки)
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in config.DATABASE_URL else {},
    echo=config.DEBUG, # В режиме DEBUG выводим все SQL-запросы в консоль
)

# Фабрика сессий — будет создавать новые сессии для каждого запроса
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для всех моделей (будет использован в models.py)
Base = declarative_base()

def get_db():
    """Генератор сессий БД для использования в эндпоинтах FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
