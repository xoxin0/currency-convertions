# Currency Exchange API

HTTP API для конвертации валют на **FastAPI + SQLite**. Сервис хранит список
валют и курсы обмена и умеет конвертировать сумму из одной валюты в другую
с поддержкой трёх сценариев расчёта: прямой курс, обратный курс и кросс-курс
через USD.

## Технологический стек

| Инструмент | Назначение |
|------------|------------|
| FastAPI    | Веб-фреймворк, авто-документация Swagger |
| SQLAlchemy | ORM (защита от SQL-инъекций) |
| SQLite     | Хранилище данных |
| Pydantic   | Валидация и сериализация |
| pytest / httpx | Тестирование |

## Структура проекта

```
currency-exchange/
├── app/
│   ├── config.py        # Настройки (переменные окружения)
│   ├── database.py      # engine, SessionLocal, Base, get_db
│   ├── models.py        # SQLAlchemy-модели (Currency, ExchangeRate)
│   ├── schemas.py       # Pydantic-схемы
│   ├── crud.py          # Операции с БД
│   ├── calculator.py    # Бизнес-логика конвертации (3 сценария)
│   ├── auth.py          # Basic Auth / API Key
│   └── main.py          # REST API эндпоинты
├── tests/               # Юнит- и интеграционные тесты
├── scripts/             # Миграции, бэкап, нагрузочный тест
├── docs/                # Документация и диаграммы
└── requirements.txt
```

## Установка и запуск

```bash
# 1. Виртуальное окружение
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\Activate.ps1     # Windows (PowerShell)

# 2. Зависимости
pip install -r requirements.txt

# 3. Запуск
uvicorn app.main:app --reload
```

После запуска доступны:

- Сервис: <http://127.0.0.1:8000>
- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

Файл БД `currencies.db` создаётся автоматически при старте.

## Переменные окружения

Скопируйте `.env.example` в `.env` и задайте значения (либо экспортируйте
переменные в окружении/`systemd`/Docker — приложение читает их через `os.getenv`):

```bash
cp .env.example .env
```

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DEBUG` | Режим отладки (вывод SQL) | `True` |
| `HOST` / `PORT` | Адрес и порт сервера | `127.0.0.1` / `8000` |
| `DATABASE_URL` | Строка подключения к БД | `sqlite:///.../currencies.db` |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | Учётные данные администратора | `admin` / `secure_password_123` |
| `API_KEY` | Ключ для мобильных эндпоинтов | `secret-api-key-for-mobile-app` |

## Основные эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| GET   | `/currencies` | Список валют |
| GET   | `/currency/{code}` | Одна валюта |
| POST  | `/currencies` | Создать валюту |
| GET   | `/exchangeRates` | Список курсов |
| GET   | `/exchangeRate/{pair}` | Курс по паре (например, `USDEUR`) |
| POST  | `/exchangeRates` | Создать курс |
| PATCH | `/exchangeRate/{pair}` | Обновить курс |
| GET   | `/exchange?from=USD&to=EUR&amount=100` | **Конвертация** |
| PATCH | `/currency/{code}/deactivate` | Деактивировать валюту (админ) |
| PATCH | `/currency/{code}/activate` | Активировать валюту (админ) |
| GET   | `/admin/stats` | Статистика системы (админ) |
| GET   | `/mobile/rates` | Курсы для мобильного клиента (API-ключ) |

## Тесты

```bash
pytest tests/ -v
```

Покрытие: модульные тесты калькулятора (11) и CRUD (11), интеграционные
тесты API (19) — всего 41 тест.

## Документация

Подробные руководства и диаграммы — в каталоге [`docs/`](docs/):
руководство пользователя, руководство администратора, диаграммы
(Use-Case, ER, Sequence), отчёты по безопасности и модификации,
матрица соответствия компетенциям.
