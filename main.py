import asyncio
import logging
from telegram.ext import Application, CommandHandler

from exchange.weex_client import WeexClient
from exchange.price_monitor import PriceMonitor, format_duration
from bot.telegram_bot import TelegramNotifier
from bot.handlers import cmd_start, cmd_stop, cmd_help, cmd_status
from config import POLL_INTERVAL, TELEGRAM_BOT_TOKEN

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def price_monitor_loop(app: Application) -> None:
    monitor = PriceMonitor()
    notifier = TelegramNotifier(bot=app.bot)

    async with WeexClient() as client:
        logger.info("Получаем список символов с WEEX...")
        symbols = await client.get_all_symbols()
        app.bot_data["symbols_count"] = len(symbols)
        logger.info("Найдено %d контрактов", len(symbols))

        try:
            await notifier.send_startup(len(symbols))
            logger.info("Сообщение о запуске разослано подписчикам")
        except Exception as e:
            logger.error("Не удалось отправить сообщение о запуске: %s", e)

        while True:
            try:
                tickers = await client.get_all_tickers()
                logger.info("Получено %d тикеров", len(tickers))

                for t in tickers:
                    symbol = t.get("symbol")
                    if not symbol:
                        continue

                    try:
                        price = float(t["lastPrice"])
                        volume = float(t.get("quoteVolume", 0) or 0)
                    except (KeyError, ValueError, TypeError):
                        continue

                    monitor.update(symbol, price, volume)
                    alerts = monitor.check_alerts(symbol)

                    for alert in alerts:
                        try:
                            alert.rsi = await client.get_rsi_1h_48h(alert.symbol)
                        except Exception as e:
                            logger.warning("RSI для %s: %s", alert.symbol, e)
                            alert.rsi = None

                        logger.info(
                            "ALERT %s %s%% за %s (≥%s%%) RSI=%s",
                            alert.symbol,
                            alert.change_percent,
                            format_duration(alert.elapsed_seconds),
                            alert.threshold,
                            alert.rsi,
                        )
                        await notifier.send_alert(alert)

            except Exception as e:
                logger.error("Ошибка в цикле: %s", e, exc_info=True)

            await asyncio.sleep(POLL_INTERVAL)


async def post_init(app: Application) -> None:
    app.create_task(price_monitor_loop(app))
    logger.info("Фоновый мониторинг цен запущен")


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise SystemExit("Задай TELEGRAM_BOT_TOKEN в .env")

    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("stop", cmd_stop))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("status", cmd_status))

    logger.info("Бот запускается (polling)...")
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()