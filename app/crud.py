"""CRUD-операции для работы с БД. Здесь только взаимодействие с базой данных, без бизнес-логики. Бизнес-логика (конвертация) — в отдельном файле calculator.py."""  # noqa: E501

from decimal import Decimal
from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Currency, ExchangeRate
from app.schemas import CurrencyCreate, ExchangeRateCreate


# ========== Валюты (Currencies) ==========
def get_all_currencies(db: Session) -> List[Currency]:
    """Получить список всех валют.
    Args: db: Сессия БД
    Returns: List[Currency]: Список всех валют (может быть пустым)
    Example: currencies = get_all_currencies(db)
    for currency in currencies: print(currency.code, currency.full_name)
    """
    return db.query(Currency).order_by(Currency.code).all()


def get_currency_by_code(db: Session, code: str) -> Optional[Currency]:
    """
    Найти валюту по её коду (например, USD, EUR).
    Args: db: Сессия БД code: Код валюты (3 буквы, регистронезависимо)
    Returns: Optional[Currency]: Найденная валюта или None
    Example: currency = get_currency_by_code(db, "USD") if currency: print(currency.sign)
    """
    # upper() — чтобы искать независимо от регистра (usd = USD)
    return db.query(Currency).filter(Currency.code == code.upper()).first()


def create_currency(db: Session, currency_data: CurrencyCreate) -> Currency:
    """Создать новую валюту.
    Args: db: Сессия БД currency_data: Данные из POST-запроса (код, имя, символ)
    Returns: Currency: Созданная валюта (с присвоенным id)
    Raises: IntegrityError: Если валюта с таким кодом уже существует
    Example: new_currency = CurrencyCreate(code="GBP", full_name="British Pound", sign="£")
    created = create_currency(db, new_currency) print(created.id)  # 4
    """
    # Преобразуем Pydantic-схему в SQLAlchemy-модель
    db_currency = Currency(
        code=currency_data.code.upper(),
        full_name=currency_data.full_name,
        sign=currency_data.sign,
    )
    db.add(db_currency)
    try:
        db.commit()  # Пытаемся сохранить
        db.refresh(db_currency)  # Загружаем сгенерированный id из БД
    except IntegrityError:
        db.rollback()  # Откатываем изменения при ошибке
        raise  # Пробрасываем исключение выше (для обработки в API)
    return db_currency


# ========== Курсы обмена (Exchange Rates) ==========
def get_all_exchange_rates(db: Session) -> List[ExchangeRate]:
    """
    Получить список всех курсов с подгруженными связанными валютами.
    Args: db: Сессия БД
    Returns: List[ExchangeRate]: Список курсов (каждый содержит base_currency и target_currency)

    Note: joinedload() — это "жадная загрузка" (eager loading). Вместо N+1 запросов (сначала курсы, потом для каждого валюту) мы делаем один запрос с JOIN.  # noqa: E501
    """
    from sqlalchemy.orm import joinedload

    return (
        db.query(ExchangeRate)
        .options(
            joinedload(ExchangeRate.base_currency),
            joinedload(ExchangeRate.target_currency),
        )
        .all()
    )


def get_exchange_rate_by_pair(
    db: Session, base_code: str, target_code: str
) -> Optional[ExchangeRate]:
    """Найти курс по паре валют (например, USD → EUR).
    Args: db: Сессия БД base_code: Код базовой валюты (например, "USD") target_code: Код целевой валюты (например, "EUR")  # noqa: E501
    Returns: Optional[ExchangeRate]: Найденный курс или None
    """
    # Сначала получаем объекты валют (чтобы знать их id)
    base_currency = get_currency_by_code(db, base_code)
    target_currency = get_currency_by_code(db, target_code)

    # Если хоть одна валюта не найдена — возвращаем None
    if not base_currency or not target_currency:
        return None
    # Ищем курс по числовым id (быстрее, чем по кодам)
    return (
        db.query(ExchangeRate)
        .filter(
            ExchangeRate.base_currency_id == base_currency.id,
            ExchangeRate.target_currency_id == target_currency.id,
        )
        .first()
    )


def create_exchange_rate(db: Session, rate_data: ExchangeRateCreate) -> ExchangeRate:
    """Создать новый курс обмена.
    Args: db: Сессия БД rate_data: Данные из POST-запроса (коды валют и курс)
    Returns: ExchangeRate: Созданный курс
    Raises: ValueError: Если одна из валют не найдена IntegrityError: Если курс для такой пары уже существует  # noqa: E501
    """
    # Находим валюты по кодам
    base_currency = get_currency_by_code(db, rate_data.base_currency_code)
    target_currency = get_currency_by_code(db, rate_data.target_currency_code)

    if not base_currency:
        raise ValueError(f"Валюта {rate_data.base_currency_code} не найдена")
    if not target_currency:
        raise ValueError(f"Валюта {rate_data.target_currency_code} не найдена")
    # Создаём курс
    db_rate = ExchangeRate(
        base_currency_id=base_currency.id,
        target_currency_id=target_currency.id,
        rate=rate_data.rate,
    )
    db.add(db_rate)
    try:
        db.commit()
        db.refresh(db_rate)
        # Подгружаем связанные валюты для ответа
        db.refresh(db_rate, attribute_names=["base_currency", "target_currency"])
    except IntegrityError:
        db.rollback()
        raise
    return db_rate


def update_exchange_rate(
    db: Session, pair: str, new_rate: Decimal  # например "USDEUR"
) -> Optional[ExchangeRate]:
    """Обновить существующий курс.
    Args: db: Сессия БД pair: Строка из 6 символов (код1 + код2), например "USDEUR" new_rate: Новое значение курса  # noqa: E501
    Returns: Optional[ExchangeRate]: Обновлённый курс или None, если не найден
    """
    # Разбираем pair на два кода: первые 3 и последние 3 символа
    if len(pair) != 6:
        raise ValueError("Pair должен быть строкой из 6 символов (например, USDEUR)")

    base_code = pair[:3]  # "USD"
    target_code = pair[3:]  # "EUR"
    # Находим курс
    rate = get_exchange_rate_by_pair(db, base_code, target_code)

    if not rate:
        return None
    # Обновляем курс
    rate.rate = new_rate
    db.commit()
    db.refresh(rate)
    return rate
