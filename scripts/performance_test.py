#!/usr/bin/env python
"""Скрипт для нагрузочного тестирования API. Измеряет производительность эндпоинтов."""

import statistics
import time
from concurrent.futures import ThreadPoolExecutor

import requests

BASE_URL = "http://127.0.0.1:8000"


def measure_response_time(
    endpoint: str, method: str = "GET", data: dict = None
) -> float:
    """Измеряет время одного запроса."""
    start_time = time.time()
    if method == "GET":
        requests.get(f"{BASE_URL}{endpoint}")
    elif method == "POST":
        requests.post(f"{BASE_URL}{endpoint}", json=data)
    else:
        raise ValueError(f"Unknown method: {method}")
    elapsed_time = time.time() - start_time
    return elapsed_time * 1000  # в миллисекундах


def run_load_test(
    endpoint: str,
    method: str = "GET",
    data: dict = None,
    iterations: int = 100,
    concurrency: int = 10,
):
    """Запускает нагрузочный тест с многопоточностью.
    Args:
        endpoint: Эндпоинт для тестирования
        method: HTTP метод
        data: Данные для POST-запроса
        iterations: Общее количество запросов
        concurrency: Количество параллельных потоков
    """
    print(f"\n{'='*60}")
    print(f" 📊 Нагрузочный тест : {method} {endpoint}")
    print(f" Запросов : {iterations}, Параллельных потоков : {concurrency}")
    print(f"{'='*60}")
    # Запускаем запросы в потоках
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = []
        for _ in range(iterations):
            future = executor.submit(measure_response_time, endpoint, method, data)
            futures.append(future)
        # Собираем результаты
        times = [f.result() for f in futures]
    # Анализ результатов
    avg_time = statistics.mean(times)
    median_time = statistics.median(times)
    min_time = min(times)
    max_time = max(times)
    p95 = statistics.quantiles(times, n=100)[94]  # 95-й перцентиль
    throughput = iterations / (sum(times) / 1000)  # запросов в секунду
    print("\n 📈 Результаты тестирования :")
    print(f" ✅ Среднее время : {avg_time:.2f} мс ")
    print(f" ✅ Медианное время : {median_time:.2f} мс ")
    print(f" 🔻 Минимальное время : {min_time:.2f} мс ")
    print(f" 🔺 Максимальное время : {max_time:.2f} мс ")
    print(f" 📊 95-й перцентиль : {p95:.2f} мс ")
    print(f" 🚀 Пропускная способность : {throughput:.1f} запросов / сек ")
    return {
        "avg": avg_time,
        "median": median_time,
        "min": min_time,
        "max": max_time,
        "p95": p95,
        "throughput": throughput,
    }


def run_all_tests():
    """Запускает все нагрузочные тесты."""
    print(" 🚀 Запуск нагрузочного тестирования Currency Exchange API")
    print(" ⚠ Убедитесь , что сервер запущен : uvicorn app.main:app")

    # Сначала добавим тестовые данные
    print("\n 📝 Подготовка тестовых данных ...")
    requests.post(
        f"{BASE_URL}/currencies",
        json={"code": "TS1", "full_name": "Test1", "sign": "T"},
    )
    requests.post(
        f"{BASE_URL}/currencies",
        json={"code": "TS2", "full_name": "Test2", "sign": "T"},
    )
    requests.post(
        f"{BASE_URL}/exchangeRates",
        json={
            "base_currency_code": "TS1",
            "target_currency_code": "TS2",
            "rate": 1.23456,
        },
    )

    # Тест 1: GET /currencies (лёгкий эндпоинт)
    run_load_test("/currencies", iterations=200, concurrency=20)

    # Тест 2: GET /exchangeRate/TS1TS2 (средний)
    run_load_test("/exchangeRate/TS1TS2", iterations=200, concurrency=20)

    # Тест 3: GET /exchange (сложная конвертация)
    run_load_test(
        "/exchange?from=TS1&to=TS2&amount=100", iterations=200, concurrency=20
    )

    # Тест 4: POST /exchangeRates (запись в БД)
    run_load_test(
        "/exchangeRates",
        method="POST",
        data={"base_currency_code": "TS2", "target_currency_code": "TS1", "rate": 0.81},
        iterations=100,
        concurrency=10,
    )

    print("\n ✅ Нагрузочное тестирование завершено ")
    print("\n 🎯 Рекомендации :")
    print("   - При throughput < 50 req/sec: рассмотрите увеличение воркеров ")
    print("   - При p95 > 1000 мс : оптимизируйте запросы к БД (добавьте индексы )")
    print("   - При max_time > 5000 мс : возможны проблемы с сетевым оборудованием ")


if __name__ == "__main__":
    run_all_tests()
