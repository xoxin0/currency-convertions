# Руководство пользователя Currency Exchange API

## Для кого это руководство
- Разработчики, интегрирующие API в свои приложения
- Администраторы, управляющие курсами валют
- Тестировщики, проверяющие работу системы

## Быстрый старт

### 1. Проверка работы сервера
```bash
curl http://api.example.com/
```

### 2. Получение всех валют
```bash
curl http://api.example.com/currencies
```

### 3. Конвертация 100 USD в EUR
```bash
curl "http://api.example.com/exchange?from=USD&to=EUR&amount=100"
```

## Примеры в разных языках

### Python (requests)
```python
import requests

response = requests.get(
    "http://api.example.com/exchange", 
    params={"from": "USD", "to": "EUR", "amount": 100}
)
print(response.json()["converted_amount"])
```

### JavaScript (fetch)
```javascript
fetch('http://api.example.com/exchange?from=USD&to=EUR&amount=100')
    .then(res => res.json())
    .then(data => console.log(data.converted_amount));
```

### cURL
```bash
curl "http://api.example.com/exchange?from=USD&to=EUR&amount=100"
```

## Часто задаваемые вопросы (FAQ)

**Вопрос:** Почему курс USD→EUR = 0.92, а не 1.086?  
**Ответ:** Курсы всегда указываются как количество целевой валюты за 1 единицу базовой.

**Вопрос:** Как добавить кросс-курс?  
**Ответ:** Не нужно. Система сама вычисляет кросс-курсы через USD.

**Вопрос:** Почему конвертация EUR→USD даёт 108.70, а не 100/0.92?  
**Ответ:** Обратный курс вычисляется как 1/0.92 = 1.086956, затем 100 * 1.086956 = 108.6956 → округление до 108.70.
