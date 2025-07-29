from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery
from fluentogram import TranslatorHub

from config import CREDITS_ADMIN_DAILY, CREDITS_USER_DAILY, ADMIN_ID


class TranslatorRunnerMiddleware(BaseMiddleware):
    def __init__(
        self,
        translator_hub_alias: str = '_translator_hub',
        translator_runner_alias: str = 'i18n',
    ):
        self.translator_hub_alias = translator_hub_alias
        self.translator_runner_alias = translator_runner_alias

    async def __call__(
        self,
        event_handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        ctx_data: Dict[str, Any],
    ) -> None:
        message = getattr(event, 'message', None)
        callback_query = getattr(event, 'callback_query', None)
        from_user = message.from_user if message else callback_query.from_user if callback_query else None

        translator_hub: Optional[TranslatorHub] = ctx_data.get(self.translator_hub_alias)

        if from_user is None or translator_hub is None:
            return await event_handler(event, ctx_data)

        user_repo = ctx_data['user_repo']
        sum_credits = CREDITS_ADMIN_DAILY if from_user.id == ADMIN_ID else CREDITS_USER_DAILY
        user = await user_repo.create_if_not_exists(telegram_id=from_user.id, balance_credits=sum_credits)

        lang = user.language if user.language else 'en'
        ctx_data[self.translator_runner_alias] = translator_hub.get_translator_by_locale(lang)
        ctx_data['user'] = user
        await event_handler(event, ctx_data)
