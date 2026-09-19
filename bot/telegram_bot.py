from telegram import Bot
from telegram.constants import ParseMode
from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    PRICE_CHANGE_THRESHOLD,
    POLL_INTERVAL,
)
from exchange.price_monitor import Alert


class TelegramNotifier:
    """Отправка алертов в Telegram."""

    def __init__(self):
        if not TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не задан в .env")
        if not TELEGRAM_CHAT_ID:
            raise ValueError("TELEGRAM_CHAT_ID не задан в .env")

        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.chat_id = TELEGRAM_CHAT_ID

    async def send_startup(self, symbols_count: int) -> None:
        """Сообщение о том, что бот запущен и готов к работе."""
        text = (
            "✅ <b>WEEX Price Alert Bot запущен</b>\n\n"
            f"📊 Контрактов в мониторинге: <b>{symbols_count}</b>\n"
            f"📈 Порог изменения: <b>{PRICE_CHANGE_THRESHOLD}%</b>\n"
            f"⏱ Интервал опроса: <b>{POLL_INTERVAL} сек</b>\n"
            f"🕐 Таймфреймы: 1м / 5м / 15м / 1ч\n\n"
            "Бот следит за резкими движениями цены и пришлёт алерт."
        )
        await self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

    async def send_alert(self, alert: Alert) -> None:
        emoji = "🟢" if alert.direction == "up" else "🔴"
        sign = "+" if alert.change_percent > 0 else ""

        text = (
            f"{emoji} <b>{alert.symbol}</b>\n"
            f"Изменение: <b>{sign}{alert.change_percent}%</b> за {alert.timeframe}\n"
            f"Цена: <code>{alert.current_price}</code>\n"
            f"Объём 24ч: <code>{self._format_volume(alert.volume_24h)} USDT</code>"
        )

        await self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

    @staticmethod
    def _format_volume(vol: float) -> str:
        if vol >= 1_000_000:
            return f"{vol / 1_000_000:.2f}M"
        if vol >= 1_000:
            return f"{vol / 1_000:.1f}K"
        return f"{vol:.0f}"