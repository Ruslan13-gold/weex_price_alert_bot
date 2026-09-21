import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "5"))

ALERT_RULES = [
    {"threshold": 2.0, "max_window": 30, "id": "2pct_30s"},
    {"threshold": 3.0, "max_window": 1 * 60, "id": "3pct_1m"},
    {"threshold": 5.0, "max_window": 2 * 60, "id": "5pct_2m"},
    {"threshold": 15.0, "max_window": 5 * 60, "id": "15pct_5m"},
    {"threshold": 20.0, "max_window": 10 * 60, "id": "20pct_10m"},
    {"threshold": 30.0, "max_window": 20 * 60, "id": "30pct_20m"},
    {"threshold": 40.0, "max_window": 30 * 60, "id": "40pct_30m"},
]

MIN_WINDOW_SECONDS = 1
ALERT_COOLDOWN = int(os.getenv("ALERT_COOLDOWN", "90"))
# Cooldown на символ целиком (сек), чтобы не спамить одной парой
SYMBOL_COOLDOWN = int(os.getenv("SYMBOL_COOLDOWN", "180"))

MIN_VOLUME_24H_USDT = float(os.getenv("MIN_VOLUME_24H_USDT", "900000"))

# RSI-пороги для классификатора сигнала
RSI_OVERBOUGHT = float(os.getenv("RSI_OVERBOUGHT", "70"))
RSI_OVERSOLD = float(os.getenv("RSI_OVERSOLD", "30"))
RSI_NEUTRAL_HIGH = float(os.getenv("RSI_NEUTRAL_HIGH", "55"))
RSI_NEUTRAL_LOW = float(os.getenv("RSI_NEUTRAL_LOW", "45"))
# Ход от этого % считается «сильным» для повышения confidence
SIGNAL_STRONG_MOVE_PCT = float(os.getenv("SIGNAL_STRONG_MOVE_PCT", "5"))

RSI_PERIOD = 14
RSI_1H_INTERVAL = "1h"
RSI_1H_LIMIT = 48
RSI_4H_INTERVAL = "4h"
RSI_4H_LIMIT = 42

WEEX_BASE_URL = "https://api-contract.weex.com"
WEEX_TICKER_URL = f"{WEEX_BASE_URL}/capi/v3/market/ticker/24hr"
WEEX_EXCHANGE_INFO_URL = f"{WEEX_BASE_URL}/capi/v3/market/exchangeInfo"
WEEX_KLINES_URL = f"{WEEX_BASE_URL}/capi/v3/market/klines"