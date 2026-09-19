import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Порог изменения цены в %
PRICE_CHANGE_THRESHOLD = float(os.getenv("PRICE_CHANGE_THRESHOLD", "2.0"))

# Интервал опроса REST API (секунды)
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "8"))

# Таймфреймы, которые мы отслеживаем (в секундах)
TIMEFRAMES = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "1h": 3600,
}

# WEEX
WEEX_BASE_URL = "https://api-contract.weex.com"
WEEX_TICKER_URL = f"{WEEX_BASE_URL}/capi/v3/market/ticker/24hr"
WEEX_EXCHANGE_INFO_URL = f"{WEEX_BASE_URL}/capi/v3/market/exchangeInfo"