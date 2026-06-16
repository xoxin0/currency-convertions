"""
Главный файл приложения. Создание таблиц БД при старте.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import engine, Base
from app.config import config

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Выполняется при старте и остановке приложения.
    Создаём таблицы, если их нет.
    """
    print("🚀 Запуск приложения...")
    # Создаём все таблицы (если не существуют)
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы (или уже существуют)")
    yield # Здесь приложение работает
    print("🛑 Остановка приложения. Очистка ресурсов...")
    # Здесь можно закрыть соединения, если нужно

# Создаём экземпляр приложения
app = FastAPI(
    title="Currency Exchange API",
    description="API для конвертации валют с поддержкой прямого, обратного и кросс-курсов",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/")
def root():
    """Корневой эндпоинт для проверки, что сервер работает"""
    return {
        "message": "Currency Exchange API",
        "docs": "/docs",
        "endpoints": [
            "GET /currencies - список валют",
            "GET /exchangeRates - список курсов",
            "GET /exchange?from=USD&to=EUR&amount=100 - конвертация"
        ]
    }
