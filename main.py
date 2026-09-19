import asyncio
import logging
from exchange.weex_client import WeexClient
from exchange.price_monitor import PriceMonitor
from bot.telegram_bot import TelegramNotifier
from config import POLL_INTERVAL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    monitor = PriceMonitor()
    notifier = TelegramNotifier()

    async with WeexClient() as client:
        logger.info("Получаем список символов с WEEX...")
        symbols = await client.get_all_symbols()
        logger.info("Найдено %d контрактов", len(symbols))

        # Уведомление о запуске
        try:
            await notifier.send_startup(len(symbols))
            logger.info("Сообщение о запуске отправлено в Telegram")
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
                        logger.info(
                            "ALERT %s %s%% за %s",
                            alert.symbol,
                            alert.change_percent,
                            alert.timeframe,
                        )
                        await notifier.send_alert(alert)

            except Exception as e:
                logger.error("Ошибка в цикле: %s", e, exc_info=True)

            await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())