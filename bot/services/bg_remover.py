from __future__ import annotations

import io
import logging

import aiohttp

from config import REMOVEBG_API_KEY

logger = logging.getLogger(__name__)

REMOVEBG_URL = "https://api.remove.bg/v1.0/removebg"


async def remove_background(image_bytes: bytes) -> bytes:
    """Удаляет фон через remove.bg API."""
    try:
        data = aiohttp.FormData()
        data.add_field(
            "image_file",
            io.BytesIO(image_bytes),
            filename="photo.jpg",
            content_type="image/jpeg",
        )
        data.add_field("size", "auto")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                REMOVEBG_URL,
                headers={"X-Api-Key": REMOVEBG_API_KEY},
                data=data,
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise RuntimeError(f"remove.bg вернул {resp.status}: {error_text}")
                return await resp.read()

    except Exception as exc:
        logger.exception("Ошибка при удалении фона: %s", exc)
        raise
