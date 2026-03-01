# PrintCard AI — Правила для Roo Code

## Проект
Telegram-бот PrintCard AI на Python.

- Принимает фото принтеров от пользователей
- Удаляет фон через rembg
- Накладывает принтер на красивый шаблонный фон через Pillow
- Возвращает готовую карточку пользователю
- Деплой: Docker-контейнер на Koyeb (Free Eco tier)

## Стек

- Python 3.11
- aiogram 3.x (Telegram Bot)
- rembg (удаление фона)
- Pillow (обработка изображений)
- openai (опционально, для описаний/GPT-фич)
- python-dotenv (переменные окружения)
- Docker (деплой на Koyeb)

## Структура проекта

```
printcard-ai/
├── .roo/
│   └── rules.md          # этот файл
├── bot/
│   ├── __init__.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── photo.py      # обработка фото
│   │   └── start.py      # /start команда
│   ├── services/
│   │   ├── __init__.py
│   │   ├── bg_remover.py # rembg логика
│   │   └── compositor.py # Pillow наложение фона
│   └── keyboards/
│       └── __init__.py
├── assets/
│   └── backgrounds/      # шаблонные фоны
├── main.py               # точка входа
├── config.py             # настройки
├── requirements.txt
├── Dockerfile
├── .env.example
└── .gitignore
```

## Правила кода

- Всегда async/await для aiogram handlers
- Обработка ошибок через try/except в каждом handler
- Логирование через logging модуль, не print()
- Переменные окружения только через python-dotenv, никаких хардкод-токенов
- Комментарии на русском языке
- Типизация везде где возможно (type hints)

## Dockerfile — ОБЯЗАТЕЛЬНО

Всегда использовать python:3.11-slim и системные зависимости:

```dockerfile
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0
```

Без этого rembg не работает на Linux (Koyeb)!

## Переменные окружения (.env)

```
BOT_TOKEN=
OPENAI_API_KEY=  # опционально
```

## Что НЕ делать

- Не хардкодить токены
- Не использовать sync requests внутри async handlers
- Не игнорировать ошибки rembg (фото может быть плохого качества)
- Не забывать закрывать файловые дескрипторы после обработки изображений
