#!/bin/bash
# Скрипт резервного копирования базы данных
# Рекомендуется запускать по расписанию (cron): 0 2 * * * /path/to/backup.sh
# Настройки
BACKUP_DIR="./backups"
DB_PATH="./currencies.db"
DATE=$(date +%Y%m%d_%H%M%S)
MAX_BACKUPS=30
# Храним последние 30 резервных копий
# Создаём папку для бэкапов, если её нет
mkdir -p "$BACKUP_DIR"
# Создаём бэкап с датой в имени
cp "$DB_PATH" "$BACKUP_DIR/currencies_backup_$DATE.db"
echo "✅ Создан бэкап : $BACKUP_DIR/currencies_backup_$DATE.db"
# Сжимаем бэкап (опционально, экономит место)
gzip "$BACKUP_DIR/currencies_backup_$DATE.db"
echo "Сжатый размер : $(du -h "$BACKUP_DIR/currencies_backup_$DATE.db.gz" | cut -f1)"
# Удаляем старые бэкапы (оставляем только MAX_BACKUPS последних)
cd "$BACKUP_DIR"
ls -t currencies_backup_*.db.gz 2>/dev/null | tail -n +$((MAX_BACKUPS + 1)) | xargs -r rm
echo "🧹 Очищены бэкапы старше $MAX_BACKUPS штук"
# Выводим список текущих бэкапов
BACKUP_COUNT=$(ls -1 currencies_backup_*.db.gz 2>/dev/null | wc -l)
echo "📊 Всего бэкапов : $BACKUP_COUNT"
