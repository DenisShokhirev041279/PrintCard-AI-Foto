from __future__ import annotations

import io
import logging

from PIL import Image

logger = logging.getLogger(__name__)

CANVAS_SIZE = (1000, 1000)  # стандарт маркетплейсов Ozon/WB/Авито

BG_COLORS = {
    "white":       (255, 255, 255, 255),
    "gray":        (240, 240, 240, 255),
    "transparent": (0,   0,   0,   0  ),
}


def composite_image(fg_bytes: bytes, bg_color: str = "white") -> bytes:
    """Накладывает изображение переднего плана на фон 1000×1000.

    :param fg_bytes: PNG с прозрачным фоном (результат rembg).
    :param bg_color: "white" | "gray" | "transparent"
    :return: JPEG (для white/gray) или PNG (для transparent) в виде bytes.
    """
    try:
        color = BG_COLORS.get(bg_color, BG_COLORS["white"])
        fg = Image.open(io.BytesIO(fg_bytes)).convert("RGBA")

        bg_w, bg_h = CANVAS_SIZE
        fg_w, fg_h = fg.size
        scale = min(bg_w * 0.85 / fg_w, bg_h * 0.85 / fg_h)
        new_w = int(fg_w * scale)
        new_h = int(fg_h * scale)
        fg = fg.resize((new_w, new_h), Image.LANCZOS)

        offset_x = (bg_w - new_w) // 2
        offset_y = (bg_h - new_h) // 2

        result = Image.new("RGBA", CANVAS_SIZE, color)
        result.paste(fg, (offset_x, offset_y), mask=fg)

        out = io.BytesIO()
        if bg_color == "transparent":
            result.save(out, format="PNG")
        else:
            result.convert("RGB").save(out, format="JPEG", quality=95)
        return out.getvalue()
    except Exception as exc:
        logger.exception("Ошибка при создании композиции: %s", exc)
        raise
