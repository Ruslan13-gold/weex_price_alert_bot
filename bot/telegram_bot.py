"""Рассылка алертов всем подписчикам."""

import logging
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import Forbidden, BadRequest
from config import TELEGRAM_BOT_TOKEN
from exchange.price_monitor import Alert, format_duration
from utils.subscribers import get_all_chat_ids, remove_subscriber

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, bot: Bot | None = None):
        if not TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не задан в .env")
        self.bot = bot or Bot(token=TELEGRAM_BOT_TOKEN)

    async def send_startup(self, symbols_count: int) -> None:
        from config import POLL_INTERVAL, ALERT_RULES

        rules_text = "\n".join(
            f"  • ≥{r['threshold']}% за 1с–{r['max_window'] // 60}м"
            for r in ALERT_RULES
        )
        text = (
            "✅ <b>WEEX Price Alert Bot запущен</b>\n\n"
            f"📊 Контрактов в мониторинге: <b>{symbols_count}</b>\n"
            f"⏱ Интервал опроса: <b>{POLL_INTERVAL} сек</b>\n\n"
            f"<b>Правила алертов:</b>\n{rules_text}\n\n"
            "В алерте: RSI(14) по 1ч свечам за 48 часов."
        )
        await self.broadcast(text)

    async def send_alert(self, alert: Alert) -> None:
        emoji = "🟢" if alert.direction == "up" else "🔴"
        sign = "+" if alert.change_percent > 0 else ""
        duration = format_duration(alert.elapsed_seconds)

        if alert.rsi is not None:
            rsi_line = f"RSI(14) 1ч / 48ч: <code>{alert.rsi}</code>"
        else:
            rsi_line = "RSI(14) 1ч / 48ч: <i>нет данных</i>"

        text = (
            f"{emoji} <b>{alert.symbol}</b>\n"
            f"Изменение: <b>{sign}{alert.change_percent}%</b> за <b>{duration}</b>\n"
            f"Правило: ≥{alert.threshold}% (окно до {self._rule_window_label(alert.rule_id)})\n"
            f"Цена: <code>{alert.current_price}</code>\n"
            f"Объём 24ч: <code>{self._format_volume(alert.volume_24h)} USDT</code>\n"
            f"{rsi_line}"
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
    def _rule_window_label(rule_id: str) -> str:
        mapping = {
            "2pct_5m": "5м",
            "5pct_10m": "10м",
            "20pct_20m": "20м",
        }
        return mapping.get(rule_id, rule_id)

    @staticmethod
    def _format_volume(vol: float) -> str:
        if vol >= 1_000_000:
            return f"{vol / 1_000_000:.2f}M"
        if vol >= 1_000:
            return f"{vol / 1_000:.1f}K"
        return f"{vol:.0f}"