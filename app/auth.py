"""Модуль аутентификации и авторизации. Реализует базовую защиту административных эндпоинтов."""

import os
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
)

# Безопасность
security_basic = HTTPBasic()
security_bearer = HTTPBearer()

# В реальном приложении пароль должен быть в .env!
# Для учебного проекта используем переменные окружения
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "secure_password_123")

# Простой токен для API-ключей (можно использовать для мобильных приложений)
API_KEY = os.getenv("API_KEY", "secret-api-key-for-mobile-app")


def verify_admin(credentials: HTTPBasicCredentials = Depends(security_basic)):
    """
    Проверка администратора через Basic Auth.
    Используется для защищённых эндпоинтов.

    В реальном проекте нужно:
    1. Хранить пароли в хэшированном виде (bcrypt)
    2. Использовать JWT-токены вместо Basic Auth
    3. Интегрироваться с системой пользователей
    Для учебного проекта — демонстрация подхода.
    """
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные имя пользователя или пароль",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def verify_api_key(auth: HTTPAuthorizationCredentials = Depends(security_bearer)):
    """
    Проверка API-ключа для мобильных приложений. Использует Bearer Token.
    """
    if auth.credentials != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный API-ключ",
        )
    return auth.credentials
