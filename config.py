import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "5"))

ALERT_RULES = [
    {"threshold": 2.0, "max_window": 5 * 60, "id": "2pct_5m"},
    {"threshold": 5.0, "max_window": 10 * 60, "id": "5pct_10m"},
    {"threshold": 20.0, "max_window": 20 * 60, "id": "20pct_20m"},
]

MIN_WINDOW_SECONDS = 1
ALERT_COOLDOWN = int(os.getenv("ALERT_COOLDOWN", "90"))

RSI_PERIOD = 14
RSI_KLINE_INTERVAL = "1h"
RSI_KLINE_LIMIT = 48

WEEX_BASE_URL = "https://api-contract.weex.com"
WEEX_TICKER_URL = f"{WEEX_BASE_URL}/capi/v3/market/ticker/24hr"
WEEX_EXCHANGE_INFO_URL = f"{WEEX_BASE_URL}/capi/v3/market/exchangeInfo"
WEEX_KLINES_URL = f"{WEEX_BASE_URL}/capi/v3/market/klines"