from __future__ import annotations

import logging

from aiogram import types, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

logger = logging.getLogger(__name__)

async def cmd_start(message: Message) -> None:
    try:
        await message.answer(
            "Привет! Отправь мне фото принтера — я удалю фон "
            "и верну готовую карточку для маркетплейса (1000×1000 px, белый фон).\n\n"
            "Как отправить:\n"
            "📷 Обычное фото — быстро, но Telegram сжимает качество\n"
            "📎 Файлом (скрепка) — оригинальное качество, лучший результат\n\n"
            "Поддерживаются JPG, PNG, WebP и другие форматы."
        )
        logger.info("Отправлено приветствие пользователю %s", message.from_user.id)
    except Exception as e:  # noqa: BLE001
        logger.exception("Ошибка в /start: %s", e)

def register_handlers(dp: Dispatcher) -> None:
    dp.message.register(cmd_start, Command("start"))
