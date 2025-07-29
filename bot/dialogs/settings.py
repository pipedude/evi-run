from aiogram_dialog.widgets.kbd import Button, Row, Group, Radio, ManagedRadio
from aiogram_dialog import Dialog, Window, ChatEvent, DialogManager
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.kbd import Cancel
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram.types import CallbackQuery
from fluentogram import TranslatorHub

from bot.dialogs.i18n_widget import I18NFormat
from bot.states.states import Settings
from database.repositories.user import UserRepository
from config import AVAILABLE_LANGUAGES_WORDS, AVAILABLE_LANGUAGES


async def on_cancel_settings(callback: ChatEvent, widget: Button, manager: DialogManager):
    await callback.message.delete()


async def on_change_language(callback: CallbackQuery, select: ManagedRadio, dialog_manager: DialogManager, data):
    if data == select.get_checked():
        return
    user = dialog_manager.middleware_data['user']
    user_repo: UserRepository = dialog_manager.middleware_data['user_repo']
    await user_repo.update(user, language=data)
    translator_hub: TranslatorHub = dialog_manager.middleware_data.get('_translator_hub')

    dialog_manager.middleware_data['i18n'] = translator_hub.get_translator_by_locale(data)


dialog = Dialog(
    # /settings
    Window(
        I18NFormat('command_settings_text'),
        Group(
            SwitchTo(
                I18NFormat('settings_language_text'),
                id='settings_language',
                state=Settings.language
            ),
            Cancel(
                I18NFormat('close_kb'),
                id='cancel_settings',
                on_click=on_cancel_settings
            ),
            width=1
        ),
        state=Settings.main,
    ),
    Window(
        I18NFormat('text_choose_lang'),
        Group(
           Radio(
                checked_text=Format('✅{item[1]}'),
                unchecked_text=Format('{item[1]}'),
                id='radio_lang',
                items=[(AVAILABLE_LANGUAGES[index], i) for index, i in enumerate(AVAILABLE_LANGUAGES_WORDS)], # [('ru', '🇷🇺Русский'), ('en', '🇺🇸English')],
                item_id_getter=lambda x: x[0],
                on_click=on_change_language
           ),
           width=2
        ),
        SwitchTo(
            I18NFormat('back_kb'),
            id='back_settings',
            state=Settings.main
        ),
        Cancel(
            I18NFormat('close_kb'),
            id='cancel_settings',
            on_click=on_cancel_settings
        ),
        state=Settings.language
    ),
)