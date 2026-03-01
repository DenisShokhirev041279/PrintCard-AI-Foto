from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
REMOVEBG_API_KEY: str = os.getenv("REMOVEBG_API_KEY", "")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан в переменных окружения")
if not REMOVEBG_API_KEY:
    raise RuntimeError("REMOVEBG_API_KEY не задан в переменных окружения")
