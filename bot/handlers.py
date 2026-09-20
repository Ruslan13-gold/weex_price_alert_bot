"""Команды Telegram-бота: /start /stop /help /status."""

from telegram import Update
from telegram.ext import ContextTypes
from utils.subscribers import add_subscriber, remove_subscriber, count_subscribers
from config import ALERT_RULES, POLL_INTERVAL, MIN_VOLUME_24H_USDT


def _rules_text() -> str:
    lines = []
    for r in ALERT_RULES:
        w = r["max_window"]
        if w < 60:
            window = f"{w}с"
        else:
            window = f"{w // 60}м"
        lines.append(f"  • ≥{r['threshold']}% за 1с–{window}")
    return "\n".join(lines)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat or not update.effective_user:
        return

    chat_id = update.effective_chat.id
    user = update.effective_user
    is_new = add_subscriber(chat_id, user.username, user.first_name)
    rules = _rules_text()
    vol_k = int(MIN_VOLUME_24H_USDT // 1000)

    if is_new:
        text = (
            "✅ <b>Подписка оформлена</b>\n\n"
            "Ты будешь получать алерты о резких движениях на WEEX Futures.\n\n"
            f"<b>Правила:</b>\n{rules}\n\n"
            f"Алерты только при объёме 24ч &gt; <b>{vol_k}k USDT</b>.\n"
            "RSI(14) 1ч/48ч и RSI(14) 4ч/7д в каждом алерте.\n\n"
            "Команды:\n"
            "/stop — отписаться\n"
            "/status — статус бота\n"
            "/help — справка"
        )
    else:
        text = (
            "ℹ️ Ты уже подписан на алерты.\n\n"
            "/stop — отписаться\n"
            "/status — статус"
        )

    await update.message.reply_text(text, parse_mode="HTML")


async def cmd_stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat:
        return

    removed = remove_subscriber(update.effective_chat.id)
    if removed:
        text = "🔕 Подписка отменена. Алерты больше не будут приходить.\n\n/start — подписаться снова"
    else:
        text = "Ты и так не был подписан.\n\n/start — подписаться"
    await update.message.reply_text(text)


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    n = count_subscribers()
    symbols_count = context.application.bot_data.get("symbols_count", "—")
    vol_k = int(MIN_VOLUME_24H_USDT // 1000)
    text = (
        "📊 <b>Статус бота</b>\n\n"
        f"Подписчиков: <b>{n}</b>\n"
        f"Контрактов в мониторинге: <b>{symbols_count}</b>\n"
        f"Интервал опроса: <b>{POLL_INTERVAL} сек</b>\n"
        f"Мин. объём 24ч: <b>{vol_k}k USDT</b>\n"
        "Биржа: WEEX Futures"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    rules = _rules_text()
    vol_k = int(MIN_VOLUME_24H_USDT // 1000)
    text = (
        "📖 <b>WEEX Price Alert Bot</b>\n\n"
        "Мониторит все фьючерсы WEEX и шлёт алерты при резких движениях цены.\n\n"
        f"<b>Правила:</b>\n{rules}\n\n"
        f"Только пары с объёмом 24ч &gt; {vol_k}k USDT.\n"
        "RSI(14) 1ч/48ч и RSI(14) 4ч/7д.\n\n"
        "<b>Команды:</b>\n"
        "/start — подписаться на алерты\n"
        "/stop — отписаться\n"
        "/status — статус\n"
        "/help — эта справка"
    )
    await update.message.reply_text(text, parse_mode="HTML")