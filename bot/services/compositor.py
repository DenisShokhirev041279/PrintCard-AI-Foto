from __future__ import annotations

import io
import logging

from PIL import Image

logger = logging.getLogger(__name__)


CANVAS_SIZE = (1000, 1000)  # стандарт маркетплейсов Ozon/WB/Авито


def composite_image(fg_bytes: bytes, bg_path: str | None = None) -> bytes:
    """Накладывает изображение переднего плана на белый фон 1000×1000.

    Масштабирует fg так, чтобы вписаться в фон с сохранением пропорций,
    и центрирует его.

    :param fg_bytes: PNG с прозрачным фоном (результат rembg).
    :param bg_path: путь к файлу кастомного фона (опционально).
    :return: результирующий PNG в виде bytes.
    """
    try:
        # белый фон 1000×1000 — стандарт российских маркетплейсов
        if bg_path:
            bg = Image.open(bg_path).convert("RGBA").resize(CANVAS_SIZE, Image.LANCZOS)
        else:
            bg = Image.new("RGBA", CANVAS_SIZE, (255, 255, 255, 255))

        fg = Image.open(io.BytesIO(fg_bytes)).convert("RGBA")

        # масштабируем fg с отступом 15% по краям
        bg_w, bg_h = CANVAS_SIZE
        fg_w, fg_h = fg.size
        padding = 0.85
        scale = min(bg_w * padding / fg_w, bg_h * padding / fg_h)
        new_w = int(fg_w * scale)
        new_h = int(fg_h * scale)
        fg = fg.resize((new_w, new_h), Image.LANCZOS)

        # центрируем
        offset_x = (bg_w - new_w) // 2
        offset_y = (bg_h - new_h) // 2

        # белая подложка + принтер
        result = Image.new("RGBA", CANVAS_SIZE, (255, 255, 255, 255))
        result.paste(bg, (0, 0), mask=bg)
        result.paste(fg, (offset_x, offset_y), mask=fg)

        out = io.BytesIO()
        result.save(out, format="PNG")
        return out.getvalue()
    except Exception as exc:
        logger.exception("Ошибка при создании композиции: %s", exc)
        raise