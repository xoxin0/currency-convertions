"""Главный файл приложения Currency Exchange API. Содержит все REST API эндпоинты."""

from contextlib import asynccontextmanager
from decimal import Decimal
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import engine, Base, get_db
from app.config import config
from app import crud, calculator
from app.schemas import (
    CurrencyCreate, CurrencyResponse,
    ExchangeRateCreate, ExchangeRateResponse,
    ExchangeRateUpdate, ExchangeRequest, ExchangeResponse
)
from app.models import Currency

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Создание таблиц БД при старте"""
    print("🚀 Запуск приложения...")
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы (или уже существуют)")
    yield
    print("🛑 Остановка приложения")

app = FastAPI(
    title="Currency Exchange API",
    description="""API для конвертации валют.

## Возможности:
- Управление списком валют (CRUD)
- Управление курсами обмена (CRUD)
- Конвертация с поддержкой:
  - Прямого курса
  - Обратного курса
  - Кросс-курса через USD

## Документация:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
""",
    version="1.0.0",
    lifespan=lifespan,
)

# ========== Корневой эндпоинт ==========
@app.get("/", tags=["System"])
def root():
    """Информация о сервере"""
    return {
        "api": "Currency Exchange API",
        "version": "1.0.0",
        "endpoints": {
            "currencies": "/currencies",
            "exchange_rates": "/exchangeRates",
            "convert": "/exchange?from=USD&to=EUR&amount=100",
            "docs": "/docs"
        }
    }

# ========== Эндпоинты для валют (Currencies) ==========
@app.get(
    "/currencies",
    response_model=List[CurrencyResponse],
    tags=["Currencies"],
    summary="Получить список всех валют",
    description="Возвращает массив всех валют, отсортированных по коду"
)
def get_currencies(db: Session = Depends(get_db)):
    """GET /currencies - список всех валют"""
    currencies = crud.get_all_currencies(db)
    return currencies

@app.get(
    "/currency/{code}",
    response_model=CurrencyResponse,
    tags=["Currencies"],
    summary="Получить одну валюту по коду",
    responses={404: {"description": "Валюта с указанным кодом не найдена"}},
    description="Возвращает валюту с указанным кодом (USD, EUR и т.д.)"
)
def get_currency(
    code: str, db: Session = Depends(get_db)
):
    """GET /currency/USD - получить валюту USD"""
    currency = crud.get_currency_by_code(db, code)
    if not currency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Валюта с кодом {code} не найдена"
        )
    return currency

@app.post(
    "/currencies",
    response_model=CurrencyResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Currencies"],
    summary="Создать новую валюту",
    responses={409: {"description": "Валюта с таким кодом уже существует"}},
    description="Добавляет новую валюту в справочник"
)
def create_currency(
    currency: CurrencyCreate, db: Session = Depends(get_db)
):
    """POST /currencies - создание валюты"""
    try:
        return crud.create_currency(db, currency)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Валюта с кодом {currency.code} уже существует"
        )

# ========== Эндпоинты для курсов (Exchange Rates) ==========
@app.get(
    "/exchangeRates",
    response_model=List[ExchangeRateResponse],
    tags=["Exchange Rates"],
    summary="Получить список всех курсов",
    description="Возвращает все курсы обмена с вложенными данными валют"
)
def get_exchange_rates(db: Session = Depends(get_db)):
    """GET /exchangeRates - список всех курсов"""
    return crud.get_all_exchange_rates(db)

@app.get(
    "/exchangeRate/{pair}",
    response_model=ExchangeRateResponse,
    tags=["Exchange Rates"],
    summary="Получить курс по паре",
    responses={
        400: {"description": "Пара должна состоять из 6 символов"},
        404: {"description": "Курс для указанной пары не найден"},
    },
    description="pair — 6 символов: первые 3 — базовая валюта, последние 3 — целевая. Пример: USDEUR"
)
def get_exchange_rate(
    pair: str, db: Session = Depends(get_db)
):
    """GET /exchangeRate/USDEUR - курс USD→EUR"""
    if len(pair) != 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пара должна быть строкой из 6 символов (например, USDEUR)"
        )
    base_code = pair[:3]
    target_code = pair[3:]
    rate = crud.get_exchange_rate_by_pair(db, base_code, target_code)
    if not rate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Курс {base_code} → {target_code} не найден"
        )
    return rate

@app.post(
    "/exchangeRates",
    response_model=ExchangeRateResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Exchange Rates"],
    summary="Создать новый курс",
    responses={
        404: {"description": "Одна из валют не найдена"},
        409: {"description": "Курс для такой пары уже существует"},
    },
    description="Создаёт курс обмена между двумя валютами"
)
def create_exchange_rate(
    rate_data: ExchangeRateCreate, db: Session = Depends(get_db)
):
    """POST /exchangeRates - создание курса"""
    try:
        return crud.create_exchange_rate(db, rate_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Курс {rate_data.base_currency_code} → {rate_data.target_currency_code} уже существует"
        )

@app.patch(
    "/exchangeRate/{pair}",
    response_model=ExchangeRateResponse,
    tags=["Exchange Rates"],
    summary="Обновить курс",
    responses={
        400: {"description": "Пара должна состоять из 6 символов"},
        404: {"description": "Курс для указанной пары не найден"},
    },
    description="Обновляет существующий курс обмена"
)
def update_exchange_rate(
    pair: str, update_data: ExchangeRateUpdate, db: Session = Depends(get_db)
):
    """PATCH /exchangeRate/USDEUR - обновить курс USD→EUR"""
    if len(pair) != 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пара должна быть строкой из 6 символов (например, USDEUR)"
        )
    updated = crud.update_exchange_rate(db, pair, update_data.rate)
    if not updated:
        base_code = pair[:3]
        target_code = pair[3:]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Курс {base_code} → {target_code} не найден"
        )
    return updated

# ========== Эндпоинт конвертации (главная бизнес-логика) ==========
@app.get(
    "/exchange",
    response_model=ExchangeResponse,
    tags=["Exchange"],
    summary="Конвертировать валюту",
    responses={404: {"description": "Валюта не найдена или курс недоступен"}},
    description="""Конвертирует указанную сумму из одной валюты в другую.

**Поддерживаемые сценарии:**
- Прямой курс (если есть USDEUR)
- Обратный курс (если есть EURUSD → используем 1/курс)
- Кросс-курс через USD (если есть USDRUB и USDEUR)

**Примеры:**
- `/exchange?from=USD&to=EUR&amount=100` -> 92.00
- `/exchange?from=EUR&to=USD&amount=100` -> 108.70
- `/exchange?from=EUR&to=RUB&amount=100` -> 8517.00
"""
)
def convert(
    from_code: str = Query(..., alias='from', min_length=3, max_length=3, description="Код исходной валюты (USD, EUR)"),
    to_code: str = Query(..., min_length=3, max_length=3, description="Код целевой валюты (RUB, GBP)"),
    amount: Decimal = Query(..., gt=0, description="Сумма для конвертации"),
    db: Session = Depends(get_db)
):
    """GET /exchange?from=USD&to=EUR&amount=100"""
    # Валидация кодов валют
    from_code = from_code.upper()
    to_code = to_code.upper()
    try:
        converted_amount, method = calculator.convert_currency(
            db, from_code, to_code, amount
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    # Получаем объекты валют для ответа
    from_currency = crud.get_currency_by_code(db, from_code)
    to_currency = crud.get_currency_by_code(db, to_code)

    # Вычисляем итоговый курс (конвертированная сумма / исходная сумма)
    rate = (converted_amount / amount).quantize(Decimal('0.000001'))

    # Добавляем в ответ информацию о методе расчёта (полезно для отладки)
    response = ExchangeResponse(
        base_currency=from_currency,
        target_currency=to_currency,
        rate=rate,
        amount=amount,
        converted_amount=converted_amount
    )
    return response
