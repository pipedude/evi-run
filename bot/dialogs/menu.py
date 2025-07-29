from aiogram_dialog.widgets.kbd import Button, Row, Group
from aiogram_dialog import Dialog, Window, ChatEvent, DialogManager
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.kbd import Cancel
from aiogram_dialog.widgets.kbd import SwitchTo

from bot.dialogs.i18n_widget import I18NFormat
from bot.states.states import Menu
from database.repositories.user import UserRepository
from bot.utils.funcs_gpt import save_user_context_txt_file, delete_user_memory, create_vectore_store


async def on_cancel_menu(callback: ChatEvent, widget: Button, manager: DialogManager):
    await callback.message.delete()


async def on_approve_new(callback: ChatEvent, widget: Button, manager: DialogManager):
    user_repo: UserRepository = manager.middleware_data['user_repo']
    i18n = manager.middleware_data.get('i18n')
    await user_repo.delete_chat_messages(manager.middleware_data['user'])

    await callback.answer(text=i18n.get('command_approve_new_text'), show_alert=True)
    await callback.message.delete()
    await manager.done()


async def on_approve_save(callback: ChatEvent, widget: Button, manager: DialogManager):
    user_repo: UserRepository = manager.middleware_data['user_repo']
    i18n = manager.middleware_data.get('i18n')
    is_save = await save_user_context_txt_file(user_repo, manager.middleware_data['user'])
    if not is_save:
        await callback.answer(text=i18n.get('warning_save_context_txt'), show_alert=True)
        return

    await user_repo.delete_chat_messages(manager.middleware_data['user'])

    await callback.answer(text=i18n.get('command_save_approve_kb'), show_alert=True)
    await callback.message.delete()
    await manager.done()


async def on_approve_delete(callback: ChatEvent, widget: Button, manager: DialogManager):
    i18n = manager.middleware_data.get('i18n')

    user_repo: UserRepository = manager.middleware_data['user_repo']
    await delete_user_memory(user_repo, manager.middleware_data['user'])
    await user_repo.delete_chat_messages(manager.middleware_data['user'])
    await create_vectore_store(user_repo, manager.middleware_data['user'])

    await callback.answer(text=i18n.get('command_delete_approve_text'), show_alert=True)
    await callback.message.delete()
    await manager.done()


dialog = Dialog(
    # /new
    Window(
        I18NFormat('command_new_text'),
        Row(
            Button(
                I18NFormat('command_new_approve_kb'),
                id='approve_new',
                on_click=on_approve_new
            ),
            SwitchTo(
                I18NFormat('command_new_save_kb'),
                id='st_save',
                state=Menu.save
            )
        ),
        Cancel(I18NFormat('close_kb'), id='cancel_menu', on_click=on_cancel_menu),
        state=Menu.new
    ),

    # /save
    Window(
        I18NFormat('command_save_text'),
        Group(
            Button(
                I18NFormat('command_new_approve_kb'),
                id='approve_save',
                on_click=on_approve_save
            ),
            Cancel(
                I18NFormat('close_kb'),
                id='cancel_menu',
                on_click=on_cancel_menu
            ),
            width=1
        ),
        state=Menu.save
    ),
    # /delete
    Window(
            I18NFormat('command_delete_text'),
            Group(
                Button(
                    I18NFormat('command_new_approve_kb'),
                    id='approve_del',
                    on_click=on_approve_delete
                ),
                Cancel(
                    I18NFormat('close_kb'),
                    id='cancel_del',
                    on_click=on_cancel_menu
                ),
                width=1
            ),
            state=Menu.delete
        )
)