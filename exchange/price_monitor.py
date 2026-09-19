import time
from collections import defaultdict, deque
from typing import Dict, Deque, Tuple, Optional, List
from dataclasses import dataclass
from config import ALERT_RULES, MIN_WINDOW_SECONDS, ALERT_COOLDOWN


@dataclass
class PricePoint:
    price: float
    volume_24h: float
    timestamp: float


@dataclass
class Alert:
    symbol: str
    change_percent: float
    elapsed_seconds: float
    current_price: float
    volume_24h: float
    direction: str
    rule_id: str
    threshold: float
    rsi: Optional[float]


def format_duration(seconds: float) -> str:
    sec = int(round(seconds))
    if sec < 60:
        return f"{sec}с"
    minutes, s = divmod(sec, 60)
    if minutes < 60:
        return f"{minutes}м {s}с" if s else f"{minutes}м"
    hours, m = divmod(minutes, 60)
    return f"{hours}ч {m}м" if m else f"{hours}ч"


def calc_rsi(closes: List[float], period: int = 14) -> Optional[float]:
    if len(closes) < period + 1:
        return None

    gains: List[float] = []
    losses: List[float] = []
    for i in range(1, len(closes)):
        delta = closes[i] - closes[i - 1]
        gains.append(max(delta, 0.0))
        losses.append(max(-delta, 0.0))

    if len(gains) < period:
        return None

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100.0 - (100.0 / (1.0 + rs)), 2)


class PriceMonitor:
    def __init__(self):
        self.max_history_seconds = max(r["max_window"] for r in ALERT_RULES) + 60
        self.history: Dict[str, Deque[PricePoint]] = defaultdict(
            lambda: deque(maxlen=600)
        )
        self.last_alert_time: Dict[Tuple[str, str], float] = {}
        self.alert_cooldown = ALERT_COOLDOWN

    def update(self, symbol: str, price: float, volume_24h: float) -> None:
        now = time.time()
        self.history[symbol].append(PricePoint(price, volume_24h, now))

        while (
            self.history[symbol]
            and now - self.history[symbol][0].timestamp > self.max_history_seconds
        ):
            self.history[symbol].popleft()

    def check_alerts(self, symbol: str) -> List[Alert]:
        points = list(self.history[symbol])
        if len(points) < 2:
            return []

        now = time.time()
        current = points[-1]
        if current.price <= 0:
            return []

        best: Optional[tuple] = None

        for rule in sorted(ALERT_RULES, key=lambda r: r["threshold"], reverse=True):
            threshold = rule["threshold"]
            max_window = rule["max_window"]
            rule_id = rule["id"]

            key = (symbol, rule_id)
            last = self.last_alert_time.get(key, 0.0)
            if now - last < self.alert_cooldown:
                continue

            best_change = 0.0
            best_elapsed = 0.0
            found = False

            for p in points:
                age = now - p.timestamp
                if age < MIN_WINDOW_SECONDS or age > max_window:
                    continue
                if p.price <= 0:
                    continue

                change = ((current.price - p.price) / p.price) * 100
                if abs(change) >= threshold and abs(change) >= abs(best_change):
                    best_change = change
                    best_elapsed = age
                    found = True

            if found:
                best = (threshold, best_change, best_elapsed, rule_id)
                break

        if not best:
            return []

        threshold, change, elapsed, rule_id = best
        self.last_alert_time[(symbol, rule_id)] = now

        return [
            Alert(
                symbol=symbol,
                change_percent=round(change, 2),
                elapsed_seconds=elapsed,
                current_price=current.price,
                volume_24h=current.volume_24h,
                direction="up" if change > 0 else "down",
                rule_id=rule_id,
                threshold=threshold,
                rsi=None,
            )
        ]