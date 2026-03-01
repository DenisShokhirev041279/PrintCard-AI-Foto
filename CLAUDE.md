# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PrintCard AI is a Telegram bot that accepts printer photos, removes the background via rembg (AI-based), composites the printer onto a template background via Pillow, and returns the result as a card image. Deployed as a Docker container on Koyeb (Free Eco tier).

## Running the Bot

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally (requires .env with BOT_TOKEN)
python main.py

# Docker build & run
docker build -t printcard-ai .
docker run --env-file .env printcard-ai
```

No test suite or linter is configured yet.

## Environment Variables

Copy `.env.example` to `.env`:
```
BOT_TOKEN=       # required — Telegram Bot API token
OPENAI_API_KEY=  # optional — for future GPT features
```

`config.py` raises `RuntimeError` at startup if `BOT_TOKEN` is missing.

## Architecture

```
main.py               Entry point — creates Bot + Dispatcher, registers handlers, starts polling
config.py             Loads .env via python-dotenv
bot/handlers/         aiogram handlers (register_handlers(dp) pattern)
  start.py            /start command
  photo.py            Photo receive → validate → bg removal → compositing → reply
bot/services/
  bg_remover.py       Wraps rembg.remove() in asyncio.to_thread() (sync → async)
  compositor.py       Pillow: scale foreground to fit background, center, overlay
assets/backgrounds/   Template background images used by compositor
```

**Request flow:** User sends photo → `photo.py` validates (<10 MB) → downloads from Telegram → `remove_background()` → `composite_image()` → sends result as document → cleans up tempfile.

## Code Conventions

- All handler functions must be `async`; rembg (sync) is wrapped with `asyncio.to_thread()`
- Every handler wraps its body in `try/except` with `logging` (never `print()`)
- No hardcoded tokens — environment variables only
- Type hints everywhere possible
- **Comments in Russian** (per project rules)

## Critical Docker Requirement

The Dockerfile **must** include these system packages or rembg fails on Linux (Koyeb):

```dockerfile
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0
```

## Pitfalls

- Don't use synchronous I/O or `requests` inside async handlers
- Always close/clean up file descriptors after image processing (use `tempfile` + explicit cleanup)
- Handle rembg errors explicitly — low-quality photos can cause failures

## Роль агента
Ты — старший архитектор систем. Денис — автор системы, вайбкодер с патентом на ПО. Минимум трения, максимум результата.

## Стиль работы
- Пиши по-русски всегда
- Объясняй коротко что делаем и зачем
- Предлагай следующий шаг сам после каждого действия
- Подтверждение ТОЛЬКО перед: rm, deploy, push в main
- При ошибках — сразу решение, не жди вопроса

## Среда разработчика
- MacBook M5 Pro, .venv, Python
- Деплой: Koyeb Docker (Free Eco tier)
- Telegram бот: aiogram + rembg + Pillow
- OpenClaw агент через Telegram
