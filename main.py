"""
Ресторанный бот для Telegram
Прототип с возможностями:
- Просмотр каталога блюд
- Поиск по названию
- Управление избранным
- Создание заказа
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_TOKEN
from handlers import menu_handlers, search_handlers, order_handlers, favorites_handlers

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Основная функция запуска бота"""
    # Инициализация бота и диспетчера
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Хранилище для FSM
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Планировщик задач
    scheduler = AsyncIOScheduler()

    # Подключение роутеров
    dp.include_router(menu_handlers.router)
    dp.include_router(search_handlers.router)
    dp.include_router(order_handlers.router)
    dp.include_router(favorites_handlers.router)

    # Запуск планировщика
    scheduler.start()

    logger.info("Бот запущен")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
