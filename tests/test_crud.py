"""Модульные тесты для CRUD-операций. Проверяем работу с базой данных на уровне функций."""

from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app import crud
from app.schemas import CurrencyCreate, ExchangeRateCreate


class TestCurrencyCRUD:
    """Тесты для валют"""

    def test_create_currency_success(self, db_session):
        """Создание валюты — успешный сценарий"""
        currency_data = CurrencyCreate(code="GBP", full_name="British Pound", sign="£")
        result = crud.create_currency(db_session, currency_data)
        assert result.id is not None
        assert result.code == "GBP"
        assert result.full_name == "British Pound"
        assert result.sign == "£"

    def test_create_currency_duplicate_code(self, db_session):
        """Создание валюты с уже существующим кодом → ошибка уникальности"""
        currency_data = CurrencyCreate(code="USD", full_name="US Dollar", sign="$")
        crud.create_currency(db_session, currency_data)
        duplicate = CurrencyCreate(code="USD", full_name="US Dollar 2", sign="$")
        with pytest.raises(IntegrityError):
            crud.create_currency(db_session, duplicate)

    def test_get_currency_by_code(self, db_session):
        """Поиск валюты по коду"""
        crud.create_currency(
            db_session, CurrencyCreate(code="JPY", full_name="Yen", sign="¥")
        )
        found = crud.get_currency_by_code(db_session, "JPY")
        assert found is not None
        assert found.code == "JPY"
        not_found = crud.get_currency_by_code(db_session, "XXX")
        assert not_found is None

    def test_get_all_currencies(self, db_session):
        """Получение списка всех валют"""
        crud.create_currency(
            db_session, CurrencyCreate(code="USD", full_name="US Dollar", sign="$")
        )
        crud.create_currency(
            db_session, CurrencyCreate(code="EUR", full_name="Euro", sign="€")
        )
        all_currencies = crud.get_all_currencies(db_session)
        assert len(all_currencies) == 2
        codes = [c.code for c in all_currencies]
        assert "USD" in codes
        assert "EUR" in codes


class TestExchangeRateCRUD:
    """Тесты для курсов обмена"""

    def test_create_exchange_rate_success(self, db_session, sample_currencies):
        """Создание курса — успешный сценарий"""
        rate_data = ExchangeRateCreate(
            base_currency_code="USD", target_currency_code="EUR", rate=Decimal("0.92")
        )
        result = crud.create_exchange_rate(db_session, rate_data)
        assert result.id is not None
        assert result.rate == Decimal("0.92")

    def test_create_exchange_rate_duplicate_pair(self, db_session, sample_currencies):
        """Создание курса для существующей пары → ошибка уникальности"""
        rate_data = ExchangeRateCreate(
            base_currency_code="USD", target_currency_code="EUR", rate=Decimal("0.92")
        )
        crud.create_exchange_rate(db_session, rate_data)
        duplicate = ExchangeRateCreate(
            base_currency_code="USD", target_currency_code="EUR", rate=Decimal("0.95")
        )
        with pytest.raises(IntegrityError):
            crud.create_exchange_rate(db_session, duplicate)

    def test_create_exchange_rate_currency_not_found(self, db_session):
        """Создание курса с несуществующей валютой → ошибка"""
        rate_data = ExchangeRateCreate(
            base_currency_code="XXX", target_currency_code="EUR", rate=Decimal("0.92")
        )
        with pytest.raises(ValueError) as exc_info:
            crud.create_exchange_rate(db_session, rate_data)
        assert "не найдена" in str(exc_info.value)

    def test_get_exchange_rate_by_pair(self, db_session, sample_currencies):
        """Поиск курса по паре валют"""
        crud.create_exchange_rate(
            db_session,
            ExchangeRateCreate(
                base_currency_code="USD",
                target_currency_code="EUR",
                rate=Decimal("0.92"),
            ),
        )
        found = crud.get_exchange_rate_by_pair(db_session, "USD", "EUR")
        assert found is not None
        assert found.rate == Decimal("0.92")
        not_found = crud.get_exchange_rate_by_pair(db_session, "USD", "RUB")
        assert not_found is None

    def test_update_exchange_rate(self, db_session, sample_currencies):
        """Обновление существующего курса"""
        crud.create_exchange_rate(
            db_session,
            ExchangeRateCreate(
                base_currency_code="USD",
                target_currency_code="EUR",
                rate=Decimal("0.92"),
            ),
        )
        updated = crud.update_exchange_rate(db_session, "USDEUR", Decimal("0.95"))
        assert updated is not None
        assert updated.rate == Decimal("0.95")
        found = crud.get_exchange_rate_by_pair(db_session, "USD", "EUR")
        assert found.rate == Decimal("0.95")

    def test_update_exchange_rate_not_found(self, db_session):
        """Обновление несуществующего курса → None"""
        updated = crud.update_exchange_rate(db_session, "USDEUR", Decimal("0.95"))
        assert updated is None
