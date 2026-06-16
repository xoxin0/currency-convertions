#!/bin/bash
# Скрипт восстановления базы данных из бэкапа
# Использование : ./scripts/restore.sh backups/currencies_backup_20240101_120000.db.gz
BACKUP_FILE=$1
if [ -z "$BACKUP_FILE" ]; then
echo "❌ Ошибка : укажите файл бэкапа"
echo "Использование : ./scripts/restore.sh путь / к / бэкапу .db.gz"
exit 1
fi
if [ ! -f "$BACKUP_FILE" ]; then
echo "❌ Файл $BACKUP_FILE не найден"
exit 1
fi
# Останавливаем приложение (если запущено)
if [ -f "app.pid" ]; then
echo "🛑 Останавливаем приложение ..."
kill $(cat app.pid)
sleep 2
fi
# Создаём бэкап текущей БД " на всякий случай "
cp currencies.db "currencies.db.backup_before_restore_$(date +%Y%m%d_%H%M%S).db"
# Восстанавливаем
if [[ $BACKUP_FILE == *.gz ]]; then
gunzip -c "$BACKUP_FILE" > currencies.db
else
cp "$BACKUP_FILE" currencies.db
fi
echo "✅ База данных восстановлена из $BACKUP_FILE"
# Запускаем приложение заново
./scripts/start.sh &
echo "🚀 Приложение перезапущено"
