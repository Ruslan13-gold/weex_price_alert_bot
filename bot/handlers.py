"""Команды Telegram-бота: /start /stop /help /status."""

from telegram import Update
from telegram.ext import ContextTypes
from utils.subscribers import add_subscriber, remove_subscriber, count_subscribers
from config import ALERT_RULES, POLL_INTERVAL


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_chat or not update.effective_user:
        return

    chat_id = update.effective_chat.id
    user = update.effective_user
    is_new = add_subscriber(chat_id, user.username, user.first_name)

    rules = "\n".join(
        f"  • ≥{r['threshold']}% за 1с–{r['max_window'] // 60}м" for r in ALERT_RULES
    )

    if is_new:
        text = (
            "✅ <b>Подписка оформлена</b>\n\n"
            "Ты будешь получать алерты о резких движениях на WEEX Futures.\n\n"
            f"<b>Правила:</b>\n{rules}\n\n"
            "В каждом алерте — цена, объём 24ч и RSI(14) по 1ч свечам за 48ч.\n\n"
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
    text = (
        "📊 <b>Статус бота</b>\n\n"
        f"Подписчиков: <b>{n}</b>\n"
        f"Контрактов в мониторинге: <b>{symbols_count}</b>\n"
        f"Интервал опроса: <b>{POLL_INTERVAL} сек</b>\n"
        "Биржа: WEEX Futures"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    rules = "\n".join(
        f"  • ≥{r['threshold']}% за 1с–{r['max_window'] // 60}м" for r in ALERT_RULES
    )
    text = (
        "📖 <b>WEEX Price Alert Bot</b>\n\n"
        "Мониторит все фьючерсы WEEX и шлёт алерты при резких движениях цены.\n\n"
        f"<b>Правила:</b>\n{rules}\n\n"
        "<b>Команды:</b>\n"
        "/start — подписаться на алерты\n"
        "/stop — отписаться\n"
        "/status — статус\n"
        "/help — эта справка"
    )
    await update.message.reply_text(text, parse_mode="HTML")