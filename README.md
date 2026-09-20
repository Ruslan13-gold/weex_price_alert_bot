# WEEX Futures Price Alert Bot

Telegram-бот, который мониторит **все фьючерсы (USDT-M perpetual)** на бирже [WEEX](https://www.weex.com) и присылает уведомления при резком изменении цены ≥ 2%.

## Возможности

- Получает список всех торговых пар через официальный API WEEX
- Опрашивает 24h-тикер всех контрактов
- Хранит историю цен и детектирует движения за **1м / 5м / 15м / 1ч**
- При изменении ≥ порога (по умолчанию 2%) отправляет сообщение в Telegram:
  - Монета
  - Процент изменения и таймфрейм
  - Текущая цена
  - Объём торгов за 24 часа (в USDT)
- Защита от спама (cooldown 2 минуты на пару + таймфрейм)
- Обработка rate-limit (HTTP 429)

## Структура проекта

```
weex_price_alert_bot/
├── .env.example          # Пример переменных окружения
├── .gitignore
├── requirements.txt
├── README.md
├── config.py             # Конфигурация
├── main.py               # Точка входа
├── bot/
│   ├── __init__.py
│   └── telegram_bot.py   # Отправка сообщений в Telegram
├── exchange/
│   ├── __init__.py
│   ├── weex_client.py    # Клиент WEEX API
│   └── price_monitor.py  # Мониторинг цен и детекция движений
└── utils/
    ├── __init__.py
    └── helpers.py
```

## Установка

1. Клонируй репозиторий:

```bash
git clone https://github.com/YOUR_USERNAME/weex_price_alert_bot.git
cd weex_price_alert_bot
```

2. Создай виртуальное окружение и установи зависимости:

```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
# или
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

3. Создай файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Заполни:

```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...   # токен от @BotFather
TELEGRAM_CHAT_ID=123456789             # твой chat_id
PRICE_CHANGE_THRESHOLD=2.0             # порог в %
POLL_INTERVAL=8                        # интервал опроса в секундах
```

### Как получить TELEGRAM_CHAT_ID

- Напиши боту @userinfobot — он вернёт твой ID
- Или временно запусти бота и посмотри `update.message.chat.id` в логах

## Запуск

```bash
python main.py
```

Бот начнёт мониторинг и будет писать алерты в указанный чат.

## Настройки

| Переменная                 | Описание                          | По умолчанию |
|----------------------------|-----------------------------------|--------------|
| `TELEGRAM_BOT_TOKEN`       | Токен Telegram-бота               | —            |
| `TELEGRAM_CHAT_ID`         | ID чата / канала для алертов      | —            |
| `PRICE_CHANGE_THRESHOLD`   | Минимальный % изменения           | `2.0`        |
| `POLL_INTERVAL`            | Интервал опроса API (сек)         | `8`          |

Таймфреймы захардкожены в `config.py`:

```python
TIMEFRAMES = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "1h": 3600,
}
```

## API WEEX

Используются публичные эндпоинты (без API-ключа):

- `GET /capi/v3/market/exchangeInfo` — список контрактов
- `GET /capi/v3/market/ticker/24hr` — тикеры всех пар

Документация: [WEEX API Docs](https://www.weex.com/api-doc)

## Лицензия

MIT
