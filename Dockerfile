# Базовый образ с Python 3.11
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY app/ ./app/
COPY tests/ ./tests/
# Копируем скрипты
COPY scripts/ ./scripts/
RUN chmod +x ./scripts/*.sh
# Открываем порт
EXPOSE 8000
# Переменные окружения
ENV DEBUG=False
ENV HOST=0.0.0.0
ENV PORT=8000
# Запуск
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
