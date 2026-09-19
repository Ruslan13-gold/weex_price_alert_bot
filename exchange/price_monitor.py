import time
from collections import defaultdict, deque
from typing import Dict, Deque, Tuple, Optional
from dataclasses import dataclass
from config import PRICE_CHANGE_THRESHOLD, TIMEFRAMES

@dataclass
class PricePoint:
    price: float
    volume_24h: float          # quoteVolume (USDT)
    timestamp: float

@dataclass
class Alert:
    symbol: str
    timeframe: str
    change_percent: float
    current_price: float
    volume_24h: float
    direction: str             # "up" / "down"

class PriceMonitor:
    def __init__(self, max_history_seconds: int = 3700):
        # symbol -> deque[(timestamp, price, volume)]
        self.history: Dict[str, Deque[PricePoint]] = defaultdict(
            lambda: deque(maxlen=500)  # достаточно для 1 часа при опросе каждые 8 сек
        )
        self.max_history_seconds = max_history_seconds
        self.last_alert_time: Dict[Tuple[str, str], float] = {}  # (symbol, tf) -> time
        self.alert_cooldown = 120  # не спамить одной и той же парой чаще чем раз в 2 мин

    def update(self, symbol: str, price: float, volume_24h: float):
        now = time.time()
        self.history[symbol].append(PricePoint(price, volume_24h, now))

        # Чистим слишком старые точки
        while self.history[symbol] and now - self.history[symbol][0].timestamp > self.max_history_seconds:
            self.history[symbol].popleft()

    def check_alerts(self, symbol: str) -> list[Alert]:
        points = self.history[symbol]
        if len(points) < 2:
            return []

        now = time.time()
        current = points[-1]
        alerts = []

        for tf_name, tf_seconds in TIMEFRAMES.items():
            # Ищем ближайшую точку ~ tf_seconds назад
            target_time = now - tf_seconds
            past_point: Optional[PricePoint] = None

            for p in reversed(points):
                if p.timestamp <= target_time:
                    past_point = p
                    break

            if not past_point:
                continue

            if past_point.price <= 0:
                continue

            change = ((current.price - past_point.price) / past_point.price) * 100

            if abs(change) >= PRICE_CHANGE_THRESHOLD:
                key = (symbol, tf_name)
                last = self.last_alert_time.get(key, 0)
                if now - last < self.alert_cooldown:
                    continue

                self.last_alert_time[key] = now
                alerts.append(Alert(
                    symbol=symbol,
                    timeframe=tf_name,
                    change_percent=round(change, 2),
                    current_price=current.price,
                    volume_24h=current.volume_24h,
                    direction="up" if change > 0 else "down"
                ))

        return alerts