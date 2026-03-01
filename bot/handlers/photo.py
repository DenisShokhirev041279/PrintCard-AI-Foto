from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from typing import cast

from aiogram import F, Bot, Dispatcher
from aiogram.enums import ChatAction
from aiogram.types import Message, FSInputFile, CallbackQuery

from bot.keyboards.bg_choice import bg_choice_keyboard
from bot.services.bg_remover import remove_background
from bot.services.compositor import composite_image

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 20_000_000

# временное хранилище вырезанных фонов: user_id -> bytes
_fg_cache: dict[int, bytes] = {}


def register_handlers(dp: Dispatcher) -> None:
    dp.message.register(photo_handler, F.photo)
    dp.message.register(document_handler, F.document.mime_type.startswith("image/"))
    dp.callback_query.register(bg_choice_handler, F.data.startswith("bg:"))


async def _download_bytes(bot: Bot, file_id: str) -> bytes | None:
    file_obj = await bot.download(file_id)
    if file_obj is None:
        return None
    if isinstance(file_obj, (bytes, bytearray)):
        return bytes(file_obj)
    if hasattr(file_obj, "read"):
        return cast(bytes, file_obj.read())
    return None


async def _process_and_ask(message: Message, bot: Bot, image_data: bytes) -> None:
    """Убирает фон, сохраняет в кэш, предлагает выбор фона."""
    fg_png = await remove_background(image_data)
    _fg_cache[message.from_user.id] = fg_png
    await message.answer(
        "Выбери фон для карточки:",
        reply_markup=bg_choice_keyboard(),
    )


async def bg_choice_handler(callback: CallbackQuery, bot: Bot) -> None:
    """Обрабатывает нажатие кнопки выбора фона."""
    await callback.answer()
    bg_color = callback.data.split(":")[1]  # "white" / "gray" / "transparent"

    fg_png = _fg_cache.get(callback.from_user.id)
    if fg_png is None:
        await callback.message.answer("Отправь фото заново — кэш устарел.")
        return

    await callback.message.edit_text("⏳ Собираю карточку...")

    result_bytes = await asyncio.to_thread(composite_image, fg_png, bg_color)

    suffix = ".png" if bg_color == "transparent" else ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(result_bytes)
        tmp.flush()
        await bot.send_document(callback.message.chat.id, FSInputFile(tmp.name))
    try:
        os.remove(tmp.name)
    except Exception:
        pass

    await callback.message.edit_text("Готово! Отправь ещё фото — сделаем новую карточку.")


async def photo_handler(message: Message, bot: Bot) -> None:
    try:
        await message.answer("⏳ Обрабатываю фото...")
        await bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)

        if not message.photo:
            await message.answer("❌ Пожалуйста, отправьте фото.")
            return

        photo = message.photo[-1]
        if photo.file_size and photo.file_size > MAX_FILE_SIZE:
            await message.answer("❌ Файл слишком большой (максимум 20 МБ).")
            return

        image_data = await _download_bytes(bot, photo.file_id)
        if image_data is None:
            await message.answer("❌ Не удалось скачать файл, попробуйте ещё раз.")
            return

        await _process_and_ask(message, bot, image_data)

    except Exception as exc:
        logger.exception("Ошибка при обработке фото: %s", exc)
        await message.answer("❌ Не удалось обработать фото, попробуйте другое.")


async def document_handler(message: Message, bot: Bot) -> None:
    try:
        doc = message.document
        if doc is None:
            return

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

        await _process_and_ask(message, bot, image_data)

    except Exception as exc:
        logger.exception("Ошибка при обработке документа: %s", exc)
        await message.answer("❌ Не удалось обработать фото, попробуйте другое.")
