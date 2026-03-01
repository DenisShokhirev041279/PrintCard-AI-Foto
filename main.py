import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN
from bot.handlers import start  # noqa: F401 импорт для регистрации
from bot.handlers import photo  # register photo handler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main() -> None:
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # регистрация обработчиков
    start.register_handlers(dp)
    photo.register_handlers(dp)

    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
    ])

    logger.info("Бот запускается")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
