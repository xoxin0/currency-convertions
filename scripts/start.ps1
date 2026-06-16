# Скрипт запуска приложения на Windows
# Использование : .\scripts\start.ps1
Write-Host "🚀 Запуск Currency Exchange API..." -ForegroundColor Green
# Переходим в корень проекта
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$ScriptDir\.."
# Активируем виртуальное окружение
.\venv\Scripts\Activate.ps1
# Переменные окружения
$env:DEBUG = "False"
$env:HOST = "0.0.0.0"
$env:PORT = "8000"
# Запуск
uvicorn app.main:app --host $env:HOST --port $env:PORT --workers 4 --loglevel info
