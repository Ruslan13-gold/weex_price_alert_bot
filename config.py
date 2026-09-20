import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "5"))

# Правила: |изменение| >= threshold за период от 1 сек до max_window
ALERT_RULES = [
    {"threshold": 2.0, "max_window": 30, "id": "2pct_30s"},       # ≥2%  за 1с–30с
    {"threshold": 3.0, "max_window": 1 * 60, "id": "3pct_1m"},     # ≥3%  за 1с–1м
    {"threshold": 5.0, "max_window": 2 * 60, "id": "5pct_2m"},     # ≥5%  за 1с–2м
    {"threshold": 15.0, "max_window": 5 * 60, "id": "15pct_5m"},   # ≥15% за 1с–5м
    {"threshold": 20.0, "max_window": 10 * 60, "id": "20pct_10m"}, # ≥20% за 1с–10м
    {"threshold": 30.0, "max_window": 20 * 60, "id": "30pct_20m"}, # ≥30% за 1с–20м
    {"threshold": 40.0, "max_window": 30 * 60, "id": "40pct_30m"}, # ≥40% за 1с–30м
]

MIN_WINDOW_SECONDS = 1
ALERT_COOLDOWN = int(os.getenv("ALERT_COOLDOWN", "90"))

# Минимальный объём торгов за 24ч (USDT)
MIN_VOLUME_24H_USDT = float(os.getenv("MIN_VOLUME_24H_USDT", "900000"))

RSI_PERIOD = 14
RSI_1H_INTERVAL = "1h"
RSI_1H_LIMIT = 48
RSI_4H_INTERVAL = "4h"
RSI_4H_LIMIT = 42

WEEX_BASE_URL = "https://api-contract.weex.com"
WEEX_TICKER_URL = f"{WEEX_BASE_URL}/capi/v3/market/ticker/24hr"
WEEX_EXCHANGE_INFO_URL = f"{WEEX_BASE_URL}/capi/v3/market/exchangeInfo"
WEEX_KLINES_URL = f"{WEEX_BASE_URL}/capi/v3/market/klines"