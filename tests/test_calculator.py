"""Модульные тесты для калькулятора конвертации валют. Проверяем все 3 сценария расчёта курса."""

from decimal import Decimal

import pytest

from app import calculator
from app.schemas import ExchangeRateCreate


class TestCalculatorDirectRate:
    """Тесты прямого курса (когда в БД есть FROM→TO)"""

    def test_direct_rate_conversion(self, db_session, sample_currencies):
        """Сценарий 1: Прямой курс. Есть курс USD→EUR = 0.92.
        Конвертируем 100 USD → должно получиться 92 EUR."""
        # Создаём курс USD→EUR
        from app import crud

        crud.create_exchange_rate(
            db_session,
            ExchangeRateCreate(
                base_currency_code="USD",
                target_currency_code="EUR",
                rate=Decimal("0.92"),
            ),
        )
        # Выполняем конвертацию
        result, method = calculator.convert_currency(
            db_session, from_code="USD", to_code="EUR", amount=Decimal("100")
        )
        # Проверки
        assert result == Decimal("92.00")
        assert method == "direct"

    def test_direct_rate_with_high_precision(self, db_session, sample_currencies):
        """Курс с высокой точностью (6 знаков).
        100 USD * 0.921234 = 92.1234 → округляется до 92.12"""
        from app import crud

        crud.create_exchange_rate(
            db_session,
            ExchangeRateCreate(
                base_currency_code="USD",
                target_currency_code="EUR",
                rate=Decimal("0.921234"),
            ),
        )
        result, method = calculator.convert_currency(
            db_session, "USD", "EUR", Decimal("100")
        )
        assert result == Decimal("92.12")
        assert method == "direct"


class TestCalculatorReverseRate:
    """Тесты обратного курса (когда есть TO→FROM, но нет FROM→TO)"""

    def test_reverse_rate_conversion(self, db_session, sample_currencies):
        """Сценарий 2: Обратный курс."""
        from app import crud

        db_session.query(crud.ExchangeRate).delete()  # Очищаем курсы
        # Создаём ТОЛЬКО курс USD→EUR
        crud.create_exchange_rate(
            db_session,
            ExchangeRateCreate(
                base_currency_code="USD",
                target_currency_code="EUR",
                rate=Decimal("0.92"),
            ),
        )
        # Конвертируем EUR → USD
        result, method = calculator.convert_currency(
            db_session, "EUR", "USD", Decimal("100")
        )
        # 100 EUR * 1.086956 = 108.6956 → округляем до 108.70
        assert result == Decimal("108.70")
        assert method == "reverse"


class TestCalculatorCrossRate:
    """Тесты кросс-курса через USD"""

    def test_cross_rate_via_usd(self, db_session, sample_currencies):
        """Сценарий 3: Кросс-курс через USD."""
        from app import crud

        db_session.query(crud.ExchangeRate).delete()
        # Создаём только курсы через USD
        crud.create_exchange_rate(
            db_session,
            ExchangeRateCreate(
                base_currency_code="USD",
                target_currency_code="EUR",
                rate=Decimal("0.92"),
            ),
        )
        crud.create_exchange_rate(
            db_session,
            ExchangeRateCreate(
                base_currency_code="USD",
                target_currency_code="RUB",
                rate=Decimal("92.50"),
            ),
        )
        # Конвертируем EUR → RUB
        result, method = calculator.convert_currency(
            db_session, "EUR", "RUB", Decimal("100")
        )
        expected = Decimal("10054.35")
        assert result == expected
        assert method == "cross_usd"

    def test_cross_rate_missing_usd_link(self, db_session, sample_currencies):
        """Если нет связи с USD ни для одной из валют — должна быть ошибка."""
        from app import crud

        crud.create_exchange_rate(
            db_session,
            ExchangeRateCreate(
                base_currency_code="USD",
                target_currency_code="EUR",
                rate=Decimal("0.92"),
            ),
        )
        with pytest.raises(ValueError) as exc_info:
            calculator.convert_currency(db_session, "EUR", "RUB", Decimal("100"))
        assert "не найден" in str(exc_info.value)


class TestCalculatorEdgeCases:
    """Пограничные случаи и обработка ошибок"""

    def test_negative_amount(self, db_session, sample_currencies):
        """Отрицательная сумма должна вызывать ошибку."""
        with pytest.raises(ValueError) as exc_info:
            calculator.convert_currency(db_session, "USD", "EUR", Decimal("-100"))
        assert "положительной" in str(exc_info.value)

    def test_zero_amount(self, db_session, sample_currencies):
        """Нулевая сумма должна вызывать ошибку."""
        with pytest.raises(ValueError) as exc_info:
            calculator.convert_currency(db_session, "USD", "EUR", Decimal("0"))
        assert "положительной" in str(exc_info.value)

    def test_same_currency(self, db_session, sample_currencies):
        """Если исходная и целевая валюта одинаковы — возвращаем ту же сумму."""
        result, method = calculator.convert_currency(
            db_session, "USD", "USD", Decimal("100")
        )
        assert result == Decimal("100.00")
        assert method == "same_currency"

    def test_currency_not_found(self, db_session):
        """Если валюта не существует в БД — ошибка."""
        with pytest.raises(ValueError) as exc_info:
            calculator.convert_currency(db_session, "XXX", "USD", Decimal("100"))
        assert "не найдена" in str(exc_info.value)

    def test_no_rate_available(self, db_session, sample_currencies):
        """Если нет ни прямого, ни обратного, ни через USD — ошибка."""
        with pytest.raises(ValueError) as exc_info:
            calculator.convert_currency(db_session, "USD", "EUR", Decimal("100"))
        assert "не найден" in str(exc_info.value)

    def test_decimal_rounding(self, db_session, sample_currencies):
        """Проверяем правильность округления (банковское округление до 2 знаков)."""
        from app import crud

        crud.create_exchange_rate(
            db_session,
            ExchangeRateCreate(
                base_currency_code="USD",
                target_currency_code="EUR",
                rate=Decimal("0.9255"),
            ),
        )
        result, _ = calculator.convert_currency(
            db_session, "USD", "EUR", Decimal("100")
        )
        assert result == Decimal("92.55")

        db_session.query(crud.ExchangeRate).delete()
        crud.create_exchange_rate(
            db_session,
            ExchangeRateCreate(
                base_currency_code="USD",
                target_currency_code="EUR",
                rate=Decimal("0.92555"),
            ),
        )
        result, _ = calculator.convert_currency(
            db_session, "USD", "EUR", Decimal("100")
        )
        assert result == Decimal("92.56")
