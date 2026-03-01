from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def bg_choice_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="⬜ Белый", callback_data="bg:white"),
        InlineKeyboardButton(text="🔘 Серый", callback_data="bg:gray"),
        InlineKeyboardButton(text="🔲 Прозрачный", callback_data="bg:transparent"),
    ]])
