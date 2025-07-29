import ast

from aiogram.enums import ContentType
from aiogram import F
from aiogram_dialog.widgets.kbd import Button, Row, Group, Radio, ManagedRadio
from aiogram_dialog import Dialog, Window, ChatEvent, DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.kbd import Cancel
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram.types import CallbackQuery, Message
from solders.keypair import Keypair
from solana.rpc.types import Pubkey
from fluentogram import TranslatorHub

from bot.dialogs.i18n_widget import I18NFormat
from bot.states.states import Wallet
from bot.utils.solana_funcs import get_balances
from database.repositories.user import UserRepository
from config import AVAILABLE_LANGUAGES_WORDS, AVAILABLE_LANGUAGES


def is_int_list(text):
    try:
        value = ast.literal_eval(text)
        if isinstance(value, list) and all(isinstance(x, int) for x in value):
            if len(value) != 0:
                return value
        return False
    except Exception:
        return False


async def on_cancel_wallet(callback: ChatEvent, widget: Button, manager: DialogManager):
    state = manager.middleware_data.get('state')
    await state.clear()
    await callback.message.delete()
    await manager.done()


async def on_input_key(message: Message, widget: MessageInput, manager: DialogManager):
    if not message.text:
        return await manager.switch_to(state=Wallet.add_not_format)
    bytes_key = is_int_list(message.text)
    if not bytes_key:
        return await manager.switch_to(state=Wallet.add_not_format)

    user_repo: UserRepository = manager.middleware_data['user_repo']
    user = manager.middleware_data['user']
    try:
        solana_client = manager.middleware_data['solana_client']
        balances, address = await get_balances(client=solana_client, secret=bytes_key)
        manager.dialog_data['balance_sol'] = '\n'.join(balances)
        manager.dialog_data['wallet_address'] = address
        await manager.switch_to(state=Wallet.balance_after_check)
        state = manager.middleware_data.get('state')
        await user_repo.add_wallet_key(user.telegram_id, message.text)
        await state.clear()
    except Exception as e:
        print(e)
        return await manager.switch_to(state=Wallet.add_not_format)


async def on_input_key_after_not_format(message: Message, widget: MessageInput, manager: DialogManager):
    if not message.text:
        return
    bytes_key = is_int_list(message.text)
    if not bytes_key:
        return
    user_repo: UserRepository = manager.middleware_data['user_repo']
    user = manager.middleware_data['user']
    try:
        solana_client = manager.middleware_data['solana_client']
        balances, address = await get_balances(client=solana_client, secret=bytes_key)
        manager.dialog_data['balance_sol'] = '\n'.join(balances)
        manager.dialog_data['wallet_address'] = address
        await manager.switch_to(state=Wallet.balance_after_check)
        state = manager.middleware_data.get('state')
        await user_repo.add_wallet_key(user.telegram_id, message.text)
        await state.clear()
    except Exception as e:
        print(e)
        pass


async def on_delete_approve(callback: ChatEvent, widget: Button, manager: DialogManager):
    user_repo: UserRepository = manager.middleware_data['user_repo']
    i18n = manager.middleware_data.get('i18n')
    user = manager.middleware_data['user']
    await user_repo.delete_wallet_key(user.telegram_id)

    await callback.answer(text=i18n.get('command_delete_key_approve_text'), show_alert=True)
    state = manager.middleware_data.get('state')
    await state.clear()
    await callback.message.delete()
    await manager.done()


async def getter_main(dialog_manager: DialogManager, **kwargs):
    user_repo: UserRepository = dialog_manager.middleware_data['user_repo']
    user = dialog_manager.middleware_data['user']
    wallet = await user_repo.get_wallet(user.telegram_id)
    return {'is_wallet': True if wallet else False}


async def getter_balance(dialog_manager: DialogManager, **kwargs):
    user_repo: UserRepository = dialog_manager.middleware_data['user_repo']
    user = dialog_manager.middleware_data['user']
    wallet = await user_repo.get_wallet(user.telegram_id)
    wallet = is_int_list(wallet)

    solana_client = dialog_manager.middleware_data['solana_client']
    balances, address = await get_balances(client=solana_client, secret=wallet)
    dialog_manager.dialog_data['balance_sol'] = '\n'.join(balances)
    dialog_manager.dialog_data['wallet_address'] = address

    state = dialog_manager.middleware_data.get('state')
    await state.clear()

    return {'balance_sol': wallet}


dialog = Dialog(
    Window(
        I18NFormat('cmd_wallet_text_start'),
        Group(
            SwitchTo(
                I18NFormat('wallet_balance_kb'),
                id='wallet_balance',
                state=Wallet.balance
            ),
            SwitchTo(
                I18NFormat('wallet_delete_key'),
                id='wallet_delete',
                state=Wallet.delete
            ),
            width=2,
            when=F['is_wallet']
        ),
        Cancel(I18NFormat('close_kb'), id='cancel_wallet', on_click=on_cancel_wallet),
        MessageInput(
            content_types=[ContentType.ANY],
            func=on_input_key
        ),
        state=Wallet.main,
        getter=getter_main
    ),
    Window(
        I18NFormat('not_format_wallet_key'),
        MessageInput(
            content_types=[ContentType.ANY],
            func=on_input_key
        ),
        Cancel(I18NFormat('close_kb'), id='cancel_wallet', on_click=on_cancel_wallet),
        state=Wallet.add_not_format
    ),
    Window(
        I18NFormat('text_after_add_key') + Format(' {dialog_data[wallet_address]}'),
        Format('{dialog_data[balance_sol]}'),
        SwitchTo(
                I18NFormat('wallet_delete_key'),
                id='wallet_delete',
                state=Wallet.delete
            ),
        Cancel(I18NFormat('close_kb'), id='cancel_wallet', on_click=on_cancel_wallet),
        state=Wallet.balance_after_check
    ),
    Window(
        I18NFormat('wallet_delete_key_text'),
        Button(
            I18NFormat('command_new_approve_kb'),
            id='wallet_delete_approve',
            on_click=on_delete_approve
        ),
        Cancel(I18NFormat('close_kb'), id='cancel_wallet', on_click=on_cancel_wallet),
        state=Wallet.delete
    ),
    Window(
        I18NFormat('text_balance_wallet') + Format(' {dialog_data[wallet_address]}'),
        Format('{dialog_data[balance_sol]}'),
        SwitchTo(
            I18NFormat('wallet_delete_key'),
            id='wallet_delete',
            state=Wallet.delete
        ),
        Cancel(I18NFormat('close_kb'), id='cancel_wallet', on_click=on_cancel_wallet),
        state=Wallet.balance,
        getter=getter_balance
    )
)