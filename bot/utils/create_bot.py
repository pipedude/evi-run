import os

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties


def get_bot(token: str) -> Bot:
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode='HTML',
                                                        link_preview_is_disabled=True
                                                        )
              )
    return bot


bot = get_bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))