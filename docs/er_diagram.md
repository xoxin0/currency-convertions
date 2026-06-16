## **ER-диаграмма: система «Обмен валют»** 

## **Сущности (таблицы)** 

## **1. currencies (валюты)** 

|**Поле**|**Тип**|**Ограничения**|**Описание**|
|---|---|---|---|
|id|INTEGER|PRIMARY KEY, AUTOINCREMENT|Уникальный идентификатор|
|code|TEXT|NOT NULL, UNIQUE|Код валюты (USD, EUR, RUB)|
|full_name|TEXT|NOT NULL|Полное название (US Dollar)|
|sign|TEXT|NOT NULL|Символ валюты ($, €,₽)|

## **Индексы:** 

- UNIQUE INDEX на code — гарантирует, что не будет двух валют с кодом USD 

## **2. exchange_rates (курсы обмена)** 

|**Поле**|**Тип**|**Ограничения**|**Описание**|
|---|---|---|---|
|id|INTEGER|PRIMARY KEY, AUTOINCREMENT|Уникальный идентификатор|
|base_currency_id|INTEGER|FOREIGN KEY → currencies(id)|Базовая валюта (например, USD)|
|target_currency_id|INTEGER|FOREIGN KEY → currencies(id)|Целевая валюта (например, EUR)|
|rate|DECIMAL(10,6)|NOT NULL, >0|Курс обмена (сколько target за 1 base)|

## **Ограничения:** 

- FOREIGN KEY (base_currency_id) REFERENCES currencies(id) ON DELETE CASCADE
- FOREIGN KEY (target_currency_id) REFERENCES currencies(id) ON DELETE CASCADE
- UNIQUE (base_currency_id, target_currency_id) — одна пара → один курс 

## **Связи между таблицами** 

currencies (1) ──────< (N) exchange_rates (base) 

currencies (1) ──────< (N) exchange_rates (target) 

## **Что это значит:** 

- Одна валюта может быть базовой во многих курсах (USD → EUR, USD → RUB)
- Одна валюта может быть целевой во многих курсах (EUR → USD, RUB → USD) 
- Связь «многие ко многим» раскрывается через таблицу-связку (но у нас просто внешние ключи) 

## **Почему DECIMAL, а не FLOAT?** 

**Ошибка новичка:** использовать FLOAT для денег. 

## **Почему нельзя:** 

0.1 + 0.2 == 0.3 # False в Python! (из-за двоичного представления)
0.1 + 0.2 # 0.30000000000000004 

**Правильно:** DECIMAL(10,6) — 10 цифр всего, 6 после запятой. Хранит деньги точно. 

## **Пример данных** 

## **currencies:** 

|**id**|**code**|**full_name**|**sign**|
|---|---|---|---|
|1|USD|US Dollar|$|
|2|EUR|Euro|€|
|3|RUB|Russian Ruble|₽|

## **exchange_rates:** 

|**id**|**base_currency_id**|**target_currency_id**|**rate**|
|---|---|---|---|
|1|1 (USD)|2 (EUR)|0.920000|
|2|1 (USD)|3 (RUB)|92.500000|
