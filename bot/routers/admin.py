from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, Filter, CommandObject
from aiogram_dialog import DialogManager, StartMode

from config import ADMIN_ID
from database.repositories.utils import UtilsRepository
import bot.keyboards.inline as inline_kb
from bot.states.states import Knowledge


class IsAdmin(Filter):
    async def __call__(self, event: Message | CallbackQuery):
        return event.from_user.id == ADMIN_ID


router = Router()


@router.message(Command('token_price'), IsAdmin())
async def token_price(message: Message, command: CommandObject, utils_repo: UtilsRepository, i18n):
    if command.args:
        try:
            price = float(command.args)
            await utils_repo.update_token_price(price)
            return await message.answer(text=i18n.get('token_price_updated_text'))
        except Exception as e:
            await message.answer(text=i18n.get('token_price_error_text'))
            return
    price_token = await utils_repo.get_token()
    if price_token:
        return await message.answer(text=f'${price_token.price_usd}', reply_markup=inline_kb.close_text(i18n.get('close_kb')))
    
    return await message.answer(text=i18n.get('not_token_price_error_text'))


@router.message(Command('knowledge'), IsAdmin())
async def cmd_knowledge(message: Message, utils_repo: UtilsRepository, i18n, dialog_manager: DialogManager):
    await dialog_manager.start(state=Knowledge.main, mode=StartMode.RESET_STACK)