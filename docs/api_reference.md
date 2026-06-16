# Полная документация API

## Валюты (Currencies)

### GET /currencies — список всех валют
**Ответ (200 OK):**
```json
[
  {
    "id": 1,
    "code": "USD",
    "full_name": "US Dollar",
    "sign": "$"
  }
]
```

### GET /currency/{code} — получить одну валюту
**Пример:** `GET /currency/USD`

### POST /currencies — создать валюту
**Тело запроса:**
```json
{
  "code": "GBP",
  "full_name": "British Pound",
  "sign": "£"
}
```

## Курсы обмена (Exchange Rates)

### GET /exchangeRates — список всех курсов
**Ответ содержит вложенные объекты валют:**
```json
[
  {
    "id": 1,
    "rate": 0.92,
    "base_currency": {"code": "USD", "full_name": "US Dollar", "sign": "$"},
    "target_currency": {"code": "EUR", "full_name": "Euro", "sign": "€"}
  }
]
```

### GET /exchangeRate/{pair} — курс по паре
**Пример:** `GET /exchangeRate/USDEUR`

### POST /exchangeRates — создать курс
**Тело запроса:**
```json
{
  "base_currency_code": "USD",
  "target_currency_code": "EUR",
  "rate": 0.92
}
```

### PATCH /exchangeRate/{pair} — обновить курс
**Пример:** `PATCH /exchangeRate/USDEUR` с телом `{"rate": 0.95}`

## Конвертация (Exchange)

### GET /exchange — главный эндпоинт
**Параметры:**
- `from` — код исходной валюты (обязательный)
- `to` — код целевой валюты (обязательный)
- `amount` — сумма для конвертации (обязательный, >0)

**Пример:** `GET /exchange?from=USD&to=EUR&amount=100`

**Ответ:**
```json
{
  "base_currency": {"code": "USD", "full_name": "US Dollar", "sign": "$"},
  "target_currency": {"code": "EUR", "full_name": "Euro", "sign": "€"},
  "rate": 0.92,
  "amount": 100,
  "converted_amount": 92.00
}
```

## Административные эндпоинты (требуют аутентификации)

### PATCH /currency/{code}/deactivate — скрыть валюту
```bash
curl -X PATCH http://api.example.com/currency/USD/deactivate \
  -u admin:your_password
```

### GET /admin/stats — статистика системы
```bash
curl http://api.example.com/admin/stats -u admin:your_password
```

## Коды ответов
| Код | Значение |
|---|---|
| 200 | OK — запрос выполнен успешно |
| 201 | Created — объект создан |
| 400 | Bad Request — неверные параметры запроса |
| 404 | Not Found — объект не найден |
| 409 | Conflict — дубликат (валюта или курс уже существует) |
| 422 | Unprocessable Entity — ошибка валидации |
| 500 | Internal Server Error — ошибка на сервере |
