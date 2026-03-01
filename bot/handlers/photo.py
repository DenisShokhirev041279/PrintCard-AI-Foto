from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from typing import cast

from aiogram import F, Bot, Dispatcher
from aiogram.enums import ChatAction
from aiogram.types import Message, FSInputFile

from bot.services.bg_remover import remove_background
from bot.services.compositor import composite_image

logger = logging.getLogger(__name__)

# лимит размера файла — 20 МБ (Telegram API максимум для документов)
MAX_FILE_SIZE = 20_000_000


def register_handlers(dp: Dispatcher) -> None:
    # обычное сжатое фото (JPEG от Telegram)
    dp.message.register(photo_handler, F.photo)
    # файл-документ с MIME image/* (оригинальный JPG/PNG/WebP/HEIC и др.)
    dp.message.register(document_handler, F.document.mime_type.startswith("image/"))


async def _download_bytes(bot: Bot, file_id: str) -> bytes | None:
    """Скачивает файл по file_id и возвращает bytes."""
    file_obj = await bot.download(file_id)
    if file_obj is None:
        return None
    if isinstance(file_obj, (bytes, bytearray)):
        return bytes(file_obj)
    if hasattr(file_obj, "read"):
        return cast(bytes, file_obj.read())
    return None


async def _process_and_reply(message: Message, bot: Bot, image_data: bytes) -> None:
    """Убирает фон, создаёт карточку и отправляет результат."""
    fg_png = await remove_background(image_data)
    result_bytes = await asyncio.to_thread(composite_image, fg_png)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(result_bytes)
        tmp.flush()
        await bot.send_document(message.chat.id, FSInputFile(tmp.name))
    try:
        os.remove(tmp.name)
    except Exception:
        pass


async def photo_handler(message: Message, bot: Bot) -> None:
    """Принимает сжатое Telegram-фото."""
    try:
        await message.answer("⏳ Обрабатываю фото...")
        await bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)

        if not message.photo:
            await message.answer("❌ Пожалуйста, отправьте фото.")
            return

        photo = message.photo[-1]  # наибольшее разрешение
        if photo.file_size and photo.file_size > MAX_FILE_SIZE:
            await message.answer("❌ Файл слишком большой (максимум 20 МБ).")
            return

        image_data = await _download_bytes(bot, photo.file_id)
        if image_data is None:
            await message.answer("❌ Не удалось скачать файл, попробуйте ещё раз.")
            return

        await _process_and_reply(message, bot, image_data)

    except Exception as exc:
        logger.exception("Ошибка при обработке фото: %s", exc)
        await message.answer("❌ Не удалось обработать фото, попробуйте другое.")


async def document_handler(message: Message, bot: Bot) -> None:
    """Принимает изображение, отправленное как файл (JPG/PNG/WebP/HEIC и др.)."""
    try:
        doc = message.document
        if doc is None:
            return

        # доп. проверка MIME на случай если фильтр пропустил что-то лишнее
        if not doc.mime_type or not doc.mime_type.startswith("image/"):
            await message.answer("❌ Поддерживаются только изображения (JPG, PNG, WebP и др.).")
            return

        if doc.file_size and doc.file_size > MAX_FILE_SIZE:
            await message.answer("❌ Файл слишком большой (максимум 20 МБ).")
            return

        await message.answer("⏳ Обрабатываю фото...")
        await bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)

        image_data = await _download_bytes(bot, doc.file_id)
        if image_data is None:
            await message.answer("❌ Не удалось скачать файл, попробуйте ещё раз.")
            return

        await _process_and_reply(message, bot, image_data)

    except Exception as exc:
        logger.exception("Ошибка при обработке документа: %s", exc)
        await message.answer("❌ Не удалось обработать фото, попробуйте другое.")
