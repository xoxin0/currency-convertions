#!/usr/bin/env python
"""Скрипт миграции : добавляет поле is_active в таблицу currencies.
Запуск : python scripts/migrate_add_is_active.py
"""

import os
import sqlite3
import sys

# Добавляем корень проекта в PATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = "currencies.db"


def migrate():
    """Добавляет колонку is_active в таблицу currencies"""
    print("Запуск миграции : добавление поля is_active")
    if not os.path.exists(DB_PATH):
        print("База данных не найдена . Сначала запустите приложение .")
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Проверяем , существует ли уже колонка
    cursor.execute("PRAGMA table_info(currencies)")
    columns = [col[1] for col in cursor.fetchall()]

    if "is_active" in columns:
        print("Поле is_active уже существует . Миграция не требуется .")
        return True

    try:
        cursor.execute(
            "ALTER TABLE currencies ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1"
        )
        conn.commit()
        print("Поле is_active успешно добавлено")
    except Exception as e:
        print(f"Ошибка миграции : {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
    return True


if __name__ == "__main__":
    if migrate():
        print("\nМиграция завершена успешно")
    else:
        print("\nМиграция не удалась")
        sys.exit(1)
