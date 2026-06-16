# Руководство администратора Currency Exchange API

## Установка системы

### Минимальные требования
- ОС: Ubuntu 20.04+ / Debian 11+ / Windows Server 2019+
- Python 3.9+ 
- 1 GB RAM 
- 5 GB свободного места

### Быстрая установка
```bash
# Клонирование
git clone https://github.com/yourusername/currency-exchange.git
cd currency-exchange

# Настройка виртуального окружения
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Настройка .env
cp .env.example .env
# Отредактируйте .env (пароль администратора)

# Запуск
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Установка как systemd-сервис (Linux)
```bash
sudo cp systemd/currency-exchange.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable currency-exchange
sudo systemctl start currency-exchange
sudo systemctl status currency-exchange
```

## Настройка

### Переменные окружения (файл .env)
| Переменная | Описание | По умолчанию |
|---|---|---|
| DEBUG | Режим отладки | False |
| HOST | Адрес для привязки | 0.0.0.0 |
| PORT | Порт сервера | 8000 |
| DATABASE_URL | URL базы данных | sqlite:///./currencies.db |
| ADMIN_USERNAME | Имя администратора | admin |
| ADMIN_PASSWORD | Пароль администратора | **Обязательно сменить!** |
| API_KEY | Ключ для мобильных приложений | **Обязательно сменить!** |

### Настройка Nginx (reverse proxy)
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Настройка HTTPS (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

## Управление базой данных

### Резервное копирование
```bash
# Ручной бэкап
./scripts/backup.sh

# Восстановление из бэкапа
./scripts/restore.sh backups/currencies_backup_20240101_120000.db.gz
```

### Автоматический бэкап (cron)
```bash
# Добавьте в crontab -e
0 2 * * * /path/to/currency-exchange/scripts/backup.sh
```

### Миграции
```bash
# Добавление нового поля
python scripts/migrate_add_is_active.py
```

## Мониторинг

### Проверка состояния
```bash
# Статус сервиса
systemctl status currency-exchange

# Просмотр логов
journalctl -u currency-exchange -f

# Статистика через API
curl -u admin:password http://localhost:8000/admin/stats
```

### Метрики производительности
```bash
# Нагрузочное тестирование
python scripts/performance_test.py

# Популярные эндпоинты
ab -n 1000 -c 10 http://localhost:8000/currencies
```

### Настройка оповещений (Prometheus + Alertmanager)
```yaml
# Пример правила для Prometheus
groups:
  - name: currency-alerts
    rules:
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 1
        annotations:
          summary: "Высокое время отклика API"
```

## Устранение неполадок

### Ошибка: «Address already in use»
**Причина:** Порт 8000 уже занят.

**Решение:**
```bash
# Найти процесс
sudo lsof -i :8000
# Убить процесс
sudo kill -9 PID
# Или сменить порт в .env
PORT=8001
```

### Ошибка: «database is locked»
**Причина:** SQLite не поддерживает высокую конкурентность.

**Решение для production:**
1. Перейти на PostgreSQL
2. Уменьшить количество воркеров: `--workers 2`

### Медленные запросы
**Диагностика:**
```bash
# Включить логирование SQL
export DEBUG=True
uvicorn app.main:app --reload

# Посмотреть долгие запросы
grep "SELECT" logs/app.log | awk '{print $NF}' | sort -n
```

**Оптимизация:**
1. Добавить индексы в БД
2. Увеличить количество воркеров
3. Использовать кэширование (Redis)

## Обновление системы
```bash
# 1. Остановить сервис
sudo systemctl stop currency-exchange

# 2. Создать бэкап
./scripts/backup.sh

# 3. Обновить код
git pull origin main

# 4. Обновить зависимости
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 5. Запустить миграции
python scripts/migrate_add_is_active.py

# 6. Запустить тесты
pytest tests/ -v

# 7. Запустить сервис
sudo systemctl start currency-exchange
```

## Контактная информация
- Техническая поддержка: support@yourdomain.com
- Репозиторий: https://github.com/yourusername/currency-exchange
- Документация API: https://api.yourdomain.com/docs
