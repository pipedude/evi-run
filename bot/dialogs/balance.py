from decimal import getcontext, Decimal
import random, os

from dotenv import load_dotenv
from aiogram_dialog.widgets.kbd import Button, Row, Group, Radio, ManagedRadio
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog import Dialog, Window, ChatEvent, DialogManager
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.kbd import Cancel
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram.types import CallbackQuery, Message
from aiogram.enums import ContentType
from fluentogram import TranslatorHub
from spl.token.instructions import get_associated_token_address
from solana.rpc.types import Pubkey

from bot.dialogs.i18n_widget import I18NFormat
from bot.states.states import Balance, Input
from database.repositories.user import UserRepository
from database.repositories.utils import UtilsRepository
from bot.utils.get_ton_course import get_ton_course
import bot.keyboards.inline as inline_kb
from config import TYPE_USAGE

load_dotenv()


def check_input_text(text: str):
    if not text:
        return
    if not text.isdigit():
        return
    if int(text) < 1:
        return
    return True


def apply_suffix(base: str, suffix: str) -> str:
    int_part, frac_part = base.split('.')
    N = len(frac_part)
    M = len(suffix)
    new_frac = frac_part[:N - M] + suffix
    return f"{int_part}.{new_frac}"


def generate_amount(usd_amount: float, rate: float, suffix: str, num_decimals: int = 9) -> str:
    getcontext().prec = 18

    ton_base = Decimal(usd_amount) / Decimal(rate)

    base_str = f"{ton_base:.{num_decimals}f}"

    result = apply_suffix(base_str, suffix)
    return result


async def on_cancel_balance(callback: ChatEvent, widget: Button, manager: DialogManager):
    state = manager.middleware_data.get('state')
    await state.clear()
    await callback.message.delete()


async def input_text_first(message: Message, widget: MessageInput, manager: DialogManager):
    if not check_input_text(message.text):
        return await manager.switch_to(state=Balance.input_not_format)
    manager.dialog_data['sum'] = message.text
    state = manager.middleware_data.get('state')
    await state.clear()
    await manager.switch_to(Balance.choose)


async def input_text_second(message: Message, widget: MessageInput, manager: DialogManager):
    if not check_input_text(message.text):
        return
    manager.dialog_data['sum'] = message.text
    state = manager.middleware_data.get('state')
    await state.clear()
    await manager.switch_to(Balance.choose)


async def on_click_add_balance(callback: ChatEvent, widget: Button, manager: DialogManager):
    state = manager.middleware_data.get('state')
    await state.set_state(Input.main)
    await manager.switch_to(Balance.input)


async def on_click_ton_type(callback: ChatEvent, widget: Button, manager: DialogManager):
    utils_repo: UtilsRepository = manager.middleware_data['utils_repo']
    user_repo: UserRepository = manager.middleware_data['user_repo']
    i18n = manager.middleware_data.get('i18n')
    while True:
        suffix = f"{random.randint(0, 9999):04d}"
        if await utils_repo.check_payment_suffix(suffix):
            break
    try:
        sum_usd = manager.dialog_data.get('sum')
        ton_course = await get_ton_course(redis=manager.middleware_data['redis'])
        generate_sum = generate_amount(usd_amount=float(sum_usd), rate=ton_course, suffix=suffix)
        payment_id = await user_repo.add_payment(callback.from_user.id, amount=int(sum_usd), crypto_amount=generate_sum,
                                                 crypto_currency='TON', random_suffix=suffix)
        await manager.done()
        await callback.message.edit_text(i18n.get('text_payment_create', sum=generate_sum, wallet=os.getenv('TON_ADDRESS')),
                                         reply_markup=inline_kb.check_payment(text=i18n.get('check_payment_kb'), payment_id=payment_id))

    except Exception as e:
        print(e)
        return await callback.answer(text=i18n.get('error_create_payment'), show_alert=True)


async def on_click_sol_type(callback: ChatEvent, widget: Button, manager: DialogManager):
    utils_repo: UtilsRepository = manager.middleware_data['utils_repo']
    user_repo: UserRepository = manager.middleware_data['user_repo']
    i18n = manager.middleware_data.get('i18n')
    token = await utils_repo.get_token()
    if not token:
        return await callback.answer(text=i18n.get('error_get_token_price'), show_alert=True)
    client_sol = manager.middleware_data['solana_client']
    ata = get_associated_token_address(mint=Pubkey.from_string(os.getenv('MINT_TOKEN_ADDRESS')),
                                       owner=Pubkey.from_string(os.getenv('ADDRESS_SOL')))

    bal_info = await client_sol.get_token_account_balance(ata, commitment="confirmed")
    decimals = bal_info.value.decimals
    while True:
        suffix = f"{random.randint(0, 9999):04d}"
        if await utils_repo.check_payment_suffix(suffix):
            break
    try:
        sum_usd = manager.dialog_data.get('sum')
        generate_sum = generate_amount(usd_amount=float(sum_usd), rate=token.price_usd, suffix=suffix, num_decimals=decimals)
        payment_id = await user_repo.add_payment(callback.from_user.id, amount=int(sum_usd), crypto_amount=generate_sum,
                                                 crypto_currency='SOL', random_suffix=suffix)
        await manager.done()
        await callback.message.edit_text(i18n.get('text_payment_create_sol', sum=generate_sum, wallet=os.getenv('ADDRESS_SOL'), token=os.getenv('MINT_TOKEN_ADDRESS')),
                                         reply_markup=inline_kb.check_payment(text=i18n.get('check_payment_kb'), payment_id=payment_id))

    except Exception as e:
        print(e)
        return await callback.answer(text=i18n.get('error_create_payment'), show_alert=True)


async def getter_balance(dialog_manager: DialogManager, **kwargs):
    user = dialog_manager.middleware_data['user']

    return {
        'balance': round(user.balance_credits, 3),
        'is_pay': True if TYPE_USAGE == 'pay' else False
    }


dialog = Dialog(
    Window(
        I18NFormat('cmd_wallet_text') + Format(' {balance} credits'),
        Button(
            I18NFormat('add_balance_kb'),
            id='choose_add_balance',
            on_click=on_click_add_balance,
            when='is_pay'
        ),
        Cancel(I18NFormat('close_kb'), id='cancel_balance', on_click=on_cancel_balance),
        state=Balance.main,
        getter=getter_balance
    ),
    Window(
        I18NFormat('text_add_balance'),
        MessageInput(
            func=input_text_first,
            content_types=[ContentType.ANY],
        ),
        Cancel(I18NFormat('close_kb'), id='cancel_balance', on_click=on_cancel_balance),
        state=Balance.input
    ),
    Window(
        I18NFormat('text_add_balance_error'),
        MessageInput(
            func=input_text_second,
            content_types=[ContentType.ANY],
        ),
        Cancel(I18NFormat('close_kb'), id='cancel_balance', on_click=on_cancel_balance),
        state=Balance.input_not_format
    ),
    Window(
        I18NFormat('choose_type_pay_text'),
        Group(
            Button(
                I18NFormat('ton_type_kb'),
                id='ton_type',
                on_click=on_click_ton_type
            ),
            Button(
                I18NFormat('sol_type_kb'),
                id='sol_type',
                on_click=on_click_sol_type
            ),
            width=2
        ),
        Cancel(I18NFormat('close_kb'), id='cancel_balance', on_click=on_cancel_balance),
        state=Balance.choose
    )
)