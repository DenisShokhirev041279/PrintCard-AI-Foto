from __future__ import annotations

import io
import logging
import asyncio

from PIL import Image, ImageFilter
from rembg import remove, new_session

logger = logging.getLogger(__name__)

# birefnet-general — SOTA-модель, лучший результат для продуктовых фото
_session = new_session("birefnet-general")


def _clean_alpha(png_bytes: bytes) -> bytes:
    """Убирает тонкие артефакты по краям: слегка эродирует альфа-канал."""
    img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    r, g, b, a = img.split()

    # размываем альфа, затем обрезаем порог — убираем полупрозрачный мусор
    a_blur = a.filter(ImageFilter.GaussianBlur(radius=1))
    a_clean = a_blur.point(lambda x: 0 if x < 30 else (255 if x > 200 else x))

    img.putalpha(a_clean)
    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()


async def remove_background(image_bytes: bytes) -> bytes:
    """Асинхронно удаляет фон из изображения.

    :param image_bytes: содержимое входного файла (любой формат),
        которое будет передано в rembg.
    :return: PNG-данные с прозрачным фоном.
    """
    try:
        result: bytes = await asyncio.to_thread(remove, image_bytes, session=_session)
        result = await asyncio.to_thread(_clean_alpha, result)
        return result
    except Exception as exc:  # noqa: BLE001
        logger.exception("Ошибка при удалении фона: %s", exc)
        raise
