# Запуск локального сервера

## Первый запуск

1 - Создание виртуальной python среды
```
python -m venv .venv
```

2 - Активация виртуальной среды
```
# PowerShell
.\.venv\Scripts\Activate.ps1
```
или
```
# CMD
.\.venv\Scripts\activate.bat
```

3 - Установка зависимостей
```
pip install -r requirements.txt
```

4 - Запуск сервера
```
uvicorn app.main:app --reload
```



## Повторный запуск

1 - Активация виртуальной среды
```
# PowerShell
.\.venv\Scripts\Activate.ps1
```
или
```
# CMD
.\.venv\Scripts\activate.bat
```

2 - Запуск сервера
```
uvicorn app.main:app --reload
```

# Документация будет доступна по ссылкам:
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/redoc