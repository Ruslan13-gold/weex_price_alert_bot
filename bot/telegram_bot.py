"""Рассылка алертов всем подписчикам."""

import logging
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import Forbidden, BadRequest
from config import TELEGRAM_BOT_TOKEN, MIN_VOLUME_24H_USDT
from exchange.price_monitor import Alert, format_duration
from utils.subscribers import get_all_chat_ids, remove_subscriber

logger = logging.getLogger(__name__)

RULE_WINDOW_LABELS = {
    "2pct_30s": "30с",
    "3pct_1m": "1м",
    "5pct_2m": "2м",
    "15pct_5m": "5м",
    "20pct_10m": "10м",
    "30pct_20m": "20м",
    "40pct_30m": "30м",
}

CONF_RU = {
    "high": "высокая",
    "medium": "средняя",
    "low": "низкая",
}


class TelegramNotifier:
    def __init__(self, bot: Bot | None = None):
        if not TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не задан в .env")
        self.bot = bot or Bot(token=TELEGRAM_BOT_TOKEN)

    async def send_startup(self, symbols_count: int) -> None:
        from config import POLL_INTERVAL, ALERT_RULES

        rules_text = "\n".join(
            f"  • ≥{r['threshold']}% за 1с–{self._window_human(r['max_window'])}"
            for r in ALERT_RULES
        )
        vol_k = int(MIN_VOLUME_24H_USDT // 1000)
        text = (
            "✅ <b>WEEX Price Alert Bot запущен</b>\n\n"
            f"📊 Контрактов: <b>{symbols_count}</b>\n"
            f"⏱ Опрос: <b>{POLL_INTERVAL} сек</b>\n"
            f"💰 Мин. объём 24ч: <b>{vol_k}k USDT</b>\n\n"
            f"<b>Триггеры:</b>\n{rules_text}\n\n"
            "В алерте: классификатор <b>LONG / SHORT</b>, RSI, идея и инвалидация.\n"
            "<i>Не финансовый совет.</i>"
        )
        await self.broadcast(text)

    async def send_alert(self, alert: Alert) -> None:
        bias = alert.signal_bias or "NEUTRAL"
        if bias == "LONG":
            bias_emoji = "🟢 LONG"
        elif bias == "SHORT":
            bias_emoji = "🔴 SHORT"
        else:
            bias_emoji = "⚪ NEUTRAL"

        conf = CONF_RU.get(alert.signal_confidence, alert.signal_confidence)
        sign = "+" if alert.change_percent > 0 else ""
        duration = format_duration(alert.elapsed_seconds)
        window = RULE_WINDOW_LABELS.get(alert.rule_id, alert.rule_id)

        rsi_1h = (
            f"<code>{alert.rsi_1h}</code>"
            if alert.rsi_1h is not None
            else "<i>нет данных</i>"
        )
        rsi_4h = (
            f"<code>{alert.rsi_4h}</code>"
            if alert.rsi_4h is not None
            else "<i>нет данных</i>"
        )

        text = (
            f"{bias_emoji} · <b>{alert.symbol}</b> · уверенность: <b>{conf}</b>\n"
            f"Score: <code>{alert.signal_score}</code>/100\n\n"
            f"Триггер: <b>{sign}{alert.change_percent}%</b> за <b>{duration}</b>\n"
            f"Правило: ≥{alert.threshold}% (окно до {window})\n"
            f"Цена: <b>{alert.current_price}</b>\n"
            f"Объём 24ч: <code>{self._format_volume(alert.volume_24h)} USDT</code>\n\n"
            f"RSI(14) 1ч / 48ч: {rsi_1h}\n"
            f"RSI(14) 4ч / 7д: {rsi_4h}\n\n"
            f"<b>Идея:</b> {alert.signal_idea}\n"
            f"<b>Горизонт:</b> {alert.signal_horizon}\n"
            f"<b>Инвалидация:</b> {alert.signal_invalidation}\n\n"
            f"<i>Потенциальный сигнал, не торговая рекомендация.</i>"
        )
        await self.broadcast(text)

    async def broadcast(self, text: str) -> None:
        chat_ids = get_all_chat_ids()
        if not chat_ids:
            logger.info("Нет подписчиков — сообщение не отправлено")
            return

        for chat_id in chat_ids:
            try:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            except Forbidden:
                logger.info("Пользователь %s заблокировал бота — удаляем", chat_id)
                remove_subscriber(chat_id)
            except BadRequest as e:
                logger.warning("BadRequest для %s: %s", chat_id, e)
            except Exception as e:
                logger.warning("Не удалось отправить %s: %s", chat_id, e)

    @staticmethod
    def _window_human(seconds: int) -> str:
        if seconds < 60:
            return f"{seconds}с"
        return f"{seconds // 60}м"

    @staticmethod
    def _format_volume(vol: float) -> str:
        if vol >= 1_000_000:
            return f"{vol / 1_000_000:.2f}M"
        if vol >= 1_000:
            return f"{vol / 1_000:.1f}K"
        return f"{vol:.0f}"