import aiohttp
import asyncio
from typing import List, Dict, Any
from config import WEEX_TICKER_URL, WEEX_EXCHANGE_INFO_URL

class WeexClient:
    def __init__(self):
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=15),
            headers={"User-Agent": "WeexPriceAlertBot/1.0"}
        )
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()

    async def get_all_symbols(self) -> List[str]:
        """Получаем все активные perpetual-контракты"""
        async with self.session.get(WEEX_EXCHANGE_INFO_URL) as resp:
            resp.raise_for_status()
            data = await resp.json()

        symbols = []
        for s in data.get("symbols", []):
            # Берём только PERPETUAL и TRADIFI_PERPETUAL
            if s.get("contractType") in ("PERPETUAL", "TRADIFI_PERPETUAL"):
                symbols.append(s["symbol"])
        return symbols

    async def get_all_tickers(self) -> List[Dict[str, Any]]:
        """Получаем 24h-тикер по всем парам"""
        async with self.session.get(WEEX_TICKER_URL) as resp:
            if resp.status == 429:
                # Rate limit — ждём
                await asyncio.sleep(5)
                return await self.get_all_tickers()
            resp.raise_for_status()
            return await resp.json()