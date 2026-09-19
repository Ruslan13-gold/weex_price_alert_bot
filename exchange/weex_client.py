import aiohttp
import asyncio
import time
from typing import List, Dict, Any, Optional
from config import (
    WEEX_TICKER_URL,
    WEEX_EXCHANGE_INFO_URL,
    WEEX_KLINES_URL,
    RSI_PERIOD,
    RSI_KLINE_INTERVAL,
    RSI_KLINE_LIMIT,
)
from exchange.price_monitor import calc_rsi


class WeexClient:
    def __init__(self):
        self.session: aiohttp.ClientSession | None = None
        self._rsi_cache: Dict[str, tuple[float, Optional[float]]] = {}
        self._rsi_cache_ttl = 300

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=15),
            headers={"User-Agent": "WeexPriceAlertBot/1.0"},
        )
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()

    async def get_all_symbols(self) -> List[str]:
        async with self.session.get(WEEX_EXCHANGE_INFO_URL) as resp:
            resp.raise_for_status()
            data = await resp.json()

        symbols = []
        for s in data.get("symbols", []):
            if s.get("contractType") in ("PERPETUAL", "TRADIFI_PERPETUAL"):
                symbols.append(s["symbol"])
        return symbols

    async def get_all_tickers(self) -> List[Dict[str, Any]]:
        async with self.session.get(WEEX_TICKER_URL) as resp:
            if resp.status == 429:
                await asyncio.sleep(5)
                return await self.get_all_tickers()
            resp.raise_for_status()
            return await resp.json()

    async def get_klines(
        self,
        symbol: str,
        interval: str = RSI_KLINE_INTERVAL,
        limit: int = RSI_KLINE_LIMIT,
    ) -> List[list]:
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
        }
        async with self.session.get(WEEX_KLINES_URL, params=params) as resp:
            if resp.status == 429:
                await asyncio.sleep(3)
                return await self.get_klines(symbol, interval, limit)
            resp.raise_for_status()
            return await resp.json()

    async def get_rsi_1h_48h(self, symbol: str) -> Optional[float]:
        now = time.time()
        cached = self._rsi_cache.get(symbol)
        if cached and now - cached[0] < self._rsi_cache_ttl:
            return cached[1]

        try:
            klines = await self.get_klines(
                symbol,
                interval=RSI_KLINE_INTERVAL,
                limit=RSI_KLINE_LIMIT,
            )
            klines_sorted = sorted(klines, key=lambda k: k[0])
            closes = [float(k[4]) for k in klines_sorted if k[4] is not None]
            rsi = calc_rsi(closes, RSI_PERIOD)
        except Exception:
            rsi = None

        self._rsi_cache[symbol] = (now, rsi)
        return rsi