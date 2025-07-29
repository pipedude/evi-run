from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import AVAILABLE_LANGUAGES


def select_language(text: list[str]):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=i, callback_data=f'select_language_{AVAILABLE_LANGUAGES[index]}') for index, i in enumerate(text)]
    ])


def close_text(text: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data='close')]
    ])


def keyboard_md(row_id: int, text: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data=f'markdown_{row_id}')]
    ])


def check_payment(text: str, payment_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data=f'check_payment_{payment_id}')]
        ]
    )
