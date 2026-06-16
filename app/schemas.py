"""Pydantic-схемы для валидации и сериализации данных."""

from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


# ========== Валюты ==========
class CurrencyBase(BaseModel):
    """Базовые поля валюты"""

    code: str = Field(..., min_length=3, max_length=3, pattern="^[A-Z]{3}$")
    full_name: str = Field(..., min_length=1, max_length=100)
    sign: str = Field(..., min_length=1, max_length=10)

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Код валюты должен состоять из 3 заглавных букв"""
        v = v.upper().strip()
        if not v.isalpha():
            raise ValueError("Код валюты должен содержать только буквы")
        if len(v) != 3:
            raise ValueError("Код валюты должен быть ровно 3 символа")
        return v


class CurrencyCreate(CurrencyBase):
    """Схема для создания валюты (POST /currencies)"""


class CurrencyResponse(CurrencyBase):
    """Схема для ответа о валюте (GET /currencies)"""

    id: int
    is_active: bool = True  # Активна ли валюта (раздел 12)

    class Config:
        from_attributes = True  # Позволяет создавать схему из SQLAlchemy-модели


# ========== Курсы обмена ==========
class ExchangeRateBase(BaseModel):
    """Базовые поля курса"""

    rate: Decimal = Field(..., gt=0, decimal_places=6)


class ExchangeRateCreate(ExchangeRateBase):
    """Схема для создания курса (POST /exchangeRates)"""

    base_currency_code: str = Field(..., min_length=3, max_length=3)
    target_currency_code: str = Field(..., min_length=3, max_length=3)

    @field_validator("base_currency_code", "target_currency_code")
    @classmethod
    def validate_currency_code(cls, v: str) -> str:
        v = v.upper().strip()
        if not v.isalpha() or len(v) != 3:
            raise ValueError("Код валюты должен быть 3 заглавные буквы")
        return v


class ExchangeRateResponse(ExchangeRateBase):
    """Схема для ответа о курсе (GET /exchangeRates)"""

    id: int
    base_currency: CurrencyResponse
    target_currency: CurrencyResponse

    class Config:
        from_attributes = True


class ExchangeRateUpdate(BaseModel):
    """Схема для обновления курса (PATCH /exchangeRate/{pair})"""

    rate: Decimal = Field(..., gt=0, decimal_places=6)


# ========== Конвертация ==========
class ExchangeRequest(BaseModel):
    """Запрос на конвертацию (GET /exchange)"""

    from_code: str = Field(..., alias="from", min_length=3, max_length=3)
    to_code: str = Field(..., min_length=3, max_length=3)
    amount: Decimal = Field(..., gt=0, decimal_places=2)

    @field_validator("from_code", "to_code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        v = v.upper().strip()
        if not v.isalpha() or len(v) != 3:
            raise ValueError("Код валюты должен быть 3 заглавные буквы")
        return v


class ExchangeResponse(BaseModel):
    """Ответ на конвертацию"""

    base_currency: CurrencyResponse
    target_currency: CurrencyResponse
    rate: Decimal
    amount: Decimal
    converted_amount: Decimal
