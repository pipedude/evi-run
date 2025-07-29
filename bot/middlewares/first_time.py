from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery

from bot.keyboards.inline import select_language
from config import AVAILABLE_LANGUAGES_WORDS


class FirstTimeMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data['user']

        if user.language:
            return await handler(event, data)

        if getattr(event, 'callback_query', None):
            if event.callback_query.data.startswith('select_language_'):
                return await handler(event, data)

        return await event.message.answer(text='Select the interface language.',
                                          reply_markup=select_language(AVAILABLE_LANGUAGES_WORDS))


