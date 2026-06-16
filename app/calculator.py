"""Модуль для конвертации валют (изолированная бизнес-логика). Содержит 3 сценария расчёта курса:
1. Прямой курс
2. Обратный курс
3. Кросс-курс через USD
Модуль не зависит от API и может тестироваться отдельно."""

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.crud import get_currency_by_code, get_exchange_rate_by_pair
from app.models import Currency

def _get_usd_rate(db: Session, currency_code: str) -> Optional[Decimal]:
    """Вспомогательная функция: получить курс валюты к USD.
    Args: db: Сессия БД currency_code: Код валюты (USD, EUR, RUB...)
    Returns: Optional[Decimal]: Курс к USD или None, если нет ни прямого, ни обратного курса Пример: Курс USD→EUR = 0.92 → для EUR _get_usd_rate = 0.92
    """
    if currency_code == "USD":
        return Decimal('1') # USD к USD = 1
    # Прямой курс: USD → валюта
    rate_direct = get_exchange_rate_by_pair(db, "USD", currency_code)
    if rate_direct:
        return rate_direct.rate

    # Обратный курс: валюта → USD
    rate_reverse = get_exchange_rate_by_pair(db, currency_code, "USD")
    if rate_reverse:
        return Decimal('1') / rate_reverse.rate
    return None

def convert_currency(
    db: Session,
    from_code: str, to_code: str, amount: Decimal
) -> Tuple[Optional[Decimal], str]:
    """Конвертировать сумму из одной валюты в другую.
    Args: db: Сессия БД from_code: Код исходной валюты (например, "USD") to_code: Код целевой валюты (например, "EUR") amount: Сумма для конвертации (положительное число)
    Returns:
    Tuple[Optional[Decimal], str]: (сконвертированная сумма, описание метода расчёта)

    Raises: ValueError: Если amount <= 0 ValueError: Если одна из валют не найдена ValueError: Если курс не найден (ни по одному сценарию)
    Методы расчёта: - "direct": прямой курс из БД - "reverse": обратный курс (1 / курс) - "cross_usd": кросс-курс через USD
    """
    # 1. Валидация суммы
    if amount <= 0:
        raise ValueError("Сумма должна быть положительной")

    # 2. Проверка, что валюты существуют
    from_currency = get_currency_by_code(db, from_code)
    to_currency = get_currency_by_code(db, to_code)

    if not from_currency:
        raise ValueError(f"Валюта {from_code} не найдена")
    if not to_currency:
        raise ValueError(f"Валюта {to_code} не найдена")

    # 3. Если исходная и целевая валюты одинаковы
    if from_code == to_code:
        return amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), "same_currency"

    # 4. Поиск курса по трём сценариям
    rate = None
    method = ""
    # Сценарий 1: Прямой курс (FROM → TO)
    direct_rate = get_exchange_rate_by_pair(db, from_code, to_code)
    if direct_rate:
        rate = direct_rate.rate
        method = "direct"
    # Сценарий 2: Обратный курс (TO → FROM)
    if rate is None:
        reverse_rate = get_exchange_rate_by_pair(db, to_code, from_code)
        if reverse_rate:
            rate = Decimal('1') / reverse_rate.rate
            method = "reverse"

    # Сценарий 3: Кросс-курс через USD
    if rate is None:
        # Получаем курсы FROM→USD и USD→TO
        from_to_usd_obj = get_exchange_rate_by_pair(db, from_code, "USD")
        usd_to_to_obj = get_exchange_rate_by_pair(db, "USD", to_code)

        from_to_usd = from_to_usd_obj.rate if from_to_usd_obj else None
        usd_to_to = usd_to_to_obj.rate if usd_to_to_obj else None

        # Или обратные варианты
        if not from_to_usd:
            # Пробуем USD→FROM
            usd_to_from = get_exchange_rate_by_pair(db, "USD", from_code)
            if usd_to_from:
                from_to_usd = Decimal('1') / usd_to_from.rate
        if not usd_to_to:
            # Пробуем TO→USD
            to_to_usd = get_exchange_rate_by_pair(db, to_code, "USD")
            if to_to_usd:
                usd_to_to = Decimal('1') / to_to_usd.rate
        # Если оба курса к USD найдены
        if from_to_usd and usd_to_to:
            # FROM → USD → TO
            rate = from_to_usd * usd_to_to
            method = "cross_usd"
    # 5. Если курс так и не найден

    if rate is None:
        raise ValueError(
            f"Курс {from_code} → {to_code} не найден "
            f"(ни прямой, ни обратный, ни через USD)"
        )
    # 6. Расчёт и округление
    converted = amount * rate
    # Округляем до 2 знаков после запятой (стандарт для валют)
    converted = converted.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return converted, method

def get_cross_rate_via_usd(db: Session, from_code: str, to_code: str) -> Optional[Decimal]:
    """Получить кросс-курс через USD (без суммы, просто курс). Полезно для демонстрации.
    Args: db: Сессия БД from_code: Код исходной валюты to_code: Код целевой валюты
    Returns: Optional[Decimal]: Кросс-курс или None
    """
    try:
        # Конвертируем 1 единицу
        converted, _ = convert_currency(db, from_code, to_code, Decimal('1'))
        return converted
    except ValueError:
        return None
