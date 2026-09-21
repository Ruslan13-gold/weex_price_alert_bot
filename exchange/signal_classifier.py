"""Классификатор потенциального сигнала LONG / SHORT / NEUTRAL.

Эвристика (не финансовый совет):
- Резкий рост + перекупленность RSI → SHORT (fade / откат)
- Резкий рост + нейтральный/низкий RSI → LONG (continuation)
- Резкое падение + перепроданность → LONG (отскок)
- Резкое падение + нейтральный/высокий RSI → SHORT (continuation)
- Противоречие 1h vs 4h RSI или слабый ход → NEUTRAL / низкая уверенность
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from config import (
    RSI_OVERBOUGHT,
    RSI_OVERSOLD,
    RSI_NEUTRAL_HIGH,
    RSI_NEUTRAL_LOW,
    SIGNAL_STRONG_MOVE_PCT,
)


@dataclass
class SignalResult:
    bias: str  # LONG | SHORT | NEUTRAL
    confidence: str  # high | medium | low
    idea: str
    horizon: str
    invalidation_hint: str
    score: int  # 0–100, условная сила гипотезы


def classify_signal(
    change_percent: float,
    rsi_1h: Optional[float],
    rsi_4h: Optional[float],
) -> SignalResult:
    up = change_percent > 0
    abs_move = abs(change_percent)
    strong = abs_move >= SIGNAL_STRONG_MOVE_PCT

    r1 = rsi_1h
    r4 = rsi_4h

    # Нет RSI — только направление импульса, низкая уверенность
    if r1 is None and r4 is None:
        if up:
            return SignalResult(
                bias="LONG",
                confidence="low",
                idea="Импульс вверх без RSI — возможен continuation, данных мало",
                horizon="15–60 мин",
                invalidation_hint="Закрепление ниже цены алерта",
                score=35,
            )
        return SignalResult(
            bias="SHORT",
            confidence="low",
            idea="Импульс вниз без RSI — возможен continuation, данных мало",
            horizon="15–60 мин",
            invalidation_hint="Закрепление выше цены алерта",
            score=35,
        )

    # Рабочие значения: 1h приоритетнее, 4h — фильтр тренда
    primary = r1 if r1 is not None else r4
    higher_tf = r4 if r4 is not None else r1

    overbought = primary is not None and primary >= RSI_OVERBOUGHT
    oversold = primary is not None and primary <= RSI_OVERSOLD
    mid_high = primary is not None and RSI_NEUTRAL_LOW <= primary < RSI_OVERBOUGHT
    mid_low = primary is not None and RSI_OVERSOLD < primary <= RSI_NEUTRAL_HIGH

    # Согласованность таймфреймов
    tf_aligned_bull = (
        r1 is not None
        and r4 is not None
        and r1 > 50
        and r4 > 50
    )
    tf_aligned_bear = (
        r1 is not None
        and r4 is not None
        and r1 < 50
        and r4 < 50
    )
    tf_conflict = (
        r1 is not None
        and r4 is not None
        and ((r1 >= 55 and r4 <= 45) or (r1 <= 45 and r4 >= 55))
    )

    # --- Рост ---
    if up:
        if overbought:
            conf = "high" if strong and (higher_tf or 0) >= 60 else "medium"
            score = 72 if conf == "high" else 58
            if tf_conflict:
                conf, score = "low", 42
            return SignalResult(
                bias="SHORT",
                confidence=conf,
                idea="Импульс вверх на перекупленности — гипотеза отката (fade)",
                horizon="15–60 мин",
                invalidation_hint="Обновление локального high и закрепление выше",
                score=score,
            )
        if oversold:
            # Рост из перепроданности — скорее long continuation / разворот вверх
            conf = "medium" if strong else "low"
            return SignalResult(
                bias="LONG",
                confidence=conf,
                idea="Отскок из перепроданности — гипотеза продолжения вверх",
                horizon="30–120 мин",
                invalidation_hint="Возврат ниже цены старта импульса",
                score=55 if strong else 40,
            )
        # Нейтральная зона RSI
        if mid_low or (primary is not None and primary < 50):
            conf = "medium" if strong and tf_aligned_bull else "low"
            return SignalResult(
                bias="LONG",
                confidence=conf,
                idea="Рост без перекупа — гипотеза continuation long",
                horizon="15–90 мин",
                invalidation_hint="Слом ниже mid импульса",
                score=60 if conf == "medium" else 45,
            )
        return SignalResult(
            bias="LONG",
            confidence="low" if tf_conflict else "medium",
            idea="Рост, RSI не экстремальный — слабый bias в long",
            horizon="15–60 мин",
            invalidation_hint="Быстрый разворот вниз > половины хода",
            score=48 if not tf_conflict else 38,
        )

    # --- Падение ---
    if oversold:
        conf = "high" if strong and (higher_tf or 100) <= 40 else "medium"
        score = 72 if conf == "high" else 58
        if tf_conflict:
            conf, score = "low", 42
        return SignalResult(
            bias="LONG",
            confidence=conf,
            idea="Импульс вниз на перепроданности — гипотеза отскока (fade)",
            horizon="15–60 мин",
            invalidation_hint="Обновление локального low и закрепление ниже",
            score=score,
        )
    if overbought:
        conf = "medium" if strong else "low"
        return SignalResult(
            bias="SHORT",
            confidence=conf,
            idea="Падение из перекупа — гипотеза continuation short",
            horizon="30–120 мин",
            invalidation_hint="Возврат выше цены старта импульса",
            score=55 if strong else 40,
        )
    if mid_high or (primary is not None and primary > 50):
        conf = "medium" if strong and tf_aligned_bear else "low"
        return SignalResult(
            bias="SHORT",
            confidence=conf,
            idea="Падение без перепроданности — гипотеза continuation short",
            horizon="15–90 мин",
            invalidation_hint="Слом выше mid импульса",
            score=60 if conf == "medium" else 45,
        )
    return SignalResult(
        bias="SHORT",
        confidence="low" if tf_conflict else "medium",
        idea="Падение, RSI не экстремальный — слабый bias в short",
        horizon="15–60 мин",
        invalidation_hint="Быстрый разворот вверх > половины хода",
        score=48 if not tf_conflict else 38,
    )