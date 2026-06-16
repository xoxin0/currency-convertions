# Отчёт о модификации системы

## Запрос заказчика
> Добавить возможность временно отключать валюты (поле is_active)

## Изменения

### 1. База данных
- Добавлено поле `is_active` в таблицу `currencies` (INTEGER, DEFAULT 1)
- Создан скрипт миграции: `scripts/migrate_add_is_active.py`

### 2. Модель данных
```python
is_active = Column(Integer, default=1, nullable=False)
```

### 3. CRUD-операции
- `get_all_currencies()`: добавлен параметр `include_inactive`
- `get_currency_by_code()`: добавлен параметр `include_inactive`
- Новые функции: `deactivate_currency()`, `activate_currency()`

### 4. API-эндпоинты
- `PATCH /currency/{code}/deactivate` — скрыть валюту
- `PATCH /currency/{code}/activate` — показать валюту

### 5. Тестирование
Добавлены тесты: `test_deactivate_currency()`
Все существующие тесты проходят ✅

### 6. Документация
Обновлено `docs/user_guide.md`
Добавлены примеры использования новых эндпоинтов

## Вывод
Изменение успешно внедрено, код протестирован, документация обновлена. Система готова к работе с новым требованием.
