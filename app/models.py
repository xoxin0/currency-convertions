"""Модели базы данных (SQLAlchemy ORM). Соответствуют ER-диаграмме из docs/er_diagram.md"""

from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Currency(Base):
    """Модель валюты. Таблица: currencies"""

    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(3), nullable=False, unique=True, index=True)  # Код: USD, EUR
    full_name = Column(String(100), nullable=False)  # US Dollar
    sign = Column(String(10), nullable=False)  # Символ: $, €, ₽

    # Связи (обратные ссылки на курсы, где эта валюта участвует)
    base_rates = relationship(
        "ExchangeRate",
        foreign_keys="ExchangeRate.base_currency_id",
        back_populates="base_currency",
        cascade="all, delete-orphan",
    )
    target_rates = relationship(
        "ExchangeRate",
        foreign_keys="ExchangeRate.target_currency_id",
        back_populates="target_currency",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Currency {self.code} ({self.full_name})>"


class ExchangeRate(Base):
    """Модель курса обмена. Таблица: exchange_rates"""

    __tablename__ = "exchange_rates"

    id = Column(Integer, primary_key=True, index=True)
    base_currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    target_currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    rate = Column(Numeric(10, 6), nullable=False)  # DECIMAL(10,6) для точности

    # Уникальность пары (базовая, целевая)
    __table_args__ = (
        UniqueConstraint(
            "base_currency_id", "target_currency_id", name="uq_currency_pair"
        ),
    )

    # Связи с валютой
    base_currency = relationship(
        "Currency", foreign_keys=[base_currency_id], back_populates="base_rates"
    )
    target_currency = relationship(
        "Currency", foreign_keys=[target_currency_id], back_populates="target_rates"
    )

    def __repr__(self):
        return f"<ExchangeRate {self.base_currency.code}-> {self.target_currency.code}: {self.rate}>"  # noqa: E501
