# Руководство по развёртыванию Currency Exchange API

## Требования к серверу
- ОС: Ubuntu 20.04+ / Debian 11+ (или Windows Server 2019+)
- Python 3.9+
- 1 GB RAM (минимум), 2 GB RAM (рекомендуется)
- 10 GB свободного дискового пространства

## Вариант 1: Локальный запуск (разработка)
1. Клонирование репозитория
```bash
git clone https://github.com/yourusername/currency-exchange.git
cd currency-exchange
```
2. Создание виртуального окружения
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```
3. Установка зависимостей
```bash
pip install -r requirements.txt
```
4. Запуск приложения
```bash
uvicorn app.main:app --reload
```
5. Проверка
Откройте браузер: http://127.0.0.1:8000/docs

## Вариант 2: Production-запуск (Ubuntu)

Шаг 1: Установка Python 3.11
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip -y
```

Шаг 2: Клонирование и настройка
```bash
git clone https://github.com/yourusername/currency-exchange.git
cd currency-exchange
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Шаг 3: Настройка .env файла
```bash
cat > .env << EOF
DEBUG=False
HOST=127.0.0.1
PORT=8000
DATABASE_URL=sqlite:///./currencies.db
EOF
```

Шаг 4: Настройка systemd-сервиса
```bash
sudo cp systemd/currency-exchange.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable currency-exchange
sudo systemctl start currency-exchange
```

Шаг 5: Настройка Nginx (reverse proxy + статика)
```bash
sudo apt install nginx -y
sudo cp docs/nginx_currency_exchange.conf /etc/nginx/sites-available/currency-exchange
sudo ln -s /etc/nginx/sites-available/currency-exchange /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Шаг 6: Настройка HTTPS (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d api.yourdomain.com
```

Настройка резервного копирования (cron)
```bash
# Добавляем задачу в crontab для ежедневного бэкапа в 2:00
crontab -e
# Добавляем строку:
0 2 * * * /path/to/currency-exchange/scripts/backup.sh
```

Проверка работоспособности
```bash
# Базовая проверка
curl http://localhost:8000/
# Просмотр логов
journalctl -u currency-exchange -f
# Мониторинг ресурсов
htop
```

Устранение неполадок
| Проблема | Решение |
|---|---|
| Порт 8000 уже занят | sudo lsof -i :8000 -> kill PID |
| Ошибка подключения к БД | Проверьте права на папку: chmod 755 ./ |
| 502 Bad Gateway (Nginx) | Проверьте, запущен ли uvicorn: systemctl status currency-exchange |
| Медленные запросы | Увеличьте количество воркеров: --workers 8 |
