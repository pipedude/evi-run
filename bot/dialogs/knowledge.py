from aiogram_dialog.widgets.kbd import Button, Row, Group, Radio, ManagedRadio
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog import Dialog, Window, ChatEvent, DialogManager
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.kbd import Cancel
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram.types import CallbackQuery, Message
from aiogram.enums import ContentType
from fluentogram import TranslatorHub

from bot.dialogs.i18n_widget import I18NFormat
from bot.states.states import Knowledge, Input
from database.repositories.utils import UtilsRepository
from bot.utils.funcs_gpt import file_to_context, delete_knowledge_base


DICT_FORMATS = {
    "doc": "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "md": "text/markdown",
    "pdf": "application/pdf",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    'txt': 'text/plain',
    'py': 'text/x-python'
}


async def on_cancel_knowledge(callback: ChatEvent, widget: Button, manager: DialogManager):
    state = manager.middleware_data.get('state')
    await state.clear()
    await callback.message.delete()


async def to_add_file(callback: ChatEvent, widget: Button, manager: DialogManager):
    state = manager.middleware_data.get('state')
    await state.set_state(Input.main)
    await manager.switch_to(state=Knowledge.add)


async def on_input_file(message: Message, widget: MessageInput, manager: DialogManager):
    utils_repo: UtilsRepository = manager.middleware_data['utils_repo']
    if not message.document:
        if manager.current_context().state == Knowledge.add_not_format:
            pass

        await manager.switch_to(state=Knowledge.add_not_format)
        return

    format_doc = message.document.file_name.split('.')[-1]
    if format_doc not in DICT_FORMATS:
        if manager.current_context().state == Knowledge.add_not_format:
            pass

        await manager.switch_to(state=Knowledge.add_not_format)
        return

    file_path = (await message.bot.get_file(file_id=message.document.file_id)).file_path
    file_bytes = (await message.bot.download_file(file_path=file_path)).read()
    answer = await file_to_context(utils_repo, message.document.file_name, file_bytes, mem_type=DICT_FORMATS.get(format_doc))
    if answer:
        state = manager.middleware_data.get('state')
        await state.clear()
        await manager.switch_to(state=Knowledge.add_approve)
    else:
        if manager.current_context().state == Knowledge.add_not_format:
            pass

        await manager.switch_to(state=Knowledge.add_not_format)
        return


async def on_delete_knowledge_base(callback: ChatEvent, widget: Button, manager: DialogManager):
    utils_repo: UtilsRepository = manager.middleware_data['utils_repo']

    await delete_knowledge_base(utils_repo)

    await manager.switch_to(state=Knowledge.delete_approve)

dialog = Dialog(
    # / knowledge main
    Window(
        I18NFormat('command_knowledge_text'),
        Group(
            Button(
                I18NFormat('command_knowledge_add_kb'),
                id='knowledge_add',
                on_click=to_add_file
            ),
            SwitchTo(
                I18NFormat('command_knowledge_delete_kb'),
                id='knowledge_delete',
                state=Knowledge.delete
            ),
            width=2,
        ),
        Cancel(I18NFormat('close_kb'), id='cancel_knowledge', on_click=on_cancel_knowledge),
        state=Knowledge.main
    ),
    # knowledge add
    Window(
        I18NFormat('command_knowledge_add_text'),
        Group(
            SwitchTo(
                I18NFormat('back_kb'),
                id='back_knowledge_add',
                state=Knowledge.main
            ),
            Cancel(I18NFormat('close_kb'), id='cancel_knowledge', on_click=on_cancel_knowledge),
            width=2
        ),
        MessageInput(
            content_types=[ContentType.ANY],
            func=on_input_file
        ),
        state=Knowledge.add
    ),
    Window(
        I18NFormat('text_not_format_file'),
        Cancel(I18NFormat('close_kb'), id='cancel_knowledge', on_click=on_cancel_knowledge),
        MessageInput(
            content_types=[ContentType.ANY],
            func=on_input_file
        ),
        state=Knowledge.add_not_format
    ),
    Window(
        I18NFormat('text_approve_file'),
        Button(I18NFormat('command_knowledge_add_kb'), id='knowledge_add', on_click=to_add_file),
        Cancel(I18NFormat('close_kb'), id='cancel_knowledge', on_click=on_cancel_knowledge),
        state=Knowledge.add_approve
    ),
    Window(
        I18NFormat('command_knowledge_delete_text'),
        Button(
            I18NFormat('command_new_approve_kb'),
            id='approve_delete',
            on_click=on_delete_knowledge_base
        ),
        Group(
            SwitchTo(
                I18NFormat('back_kb'),
                id='back_knowledge_delete',
                state=Knowledge.main
            ),
            Cancel(I18NFormat('close_kb'), id='cancel_knowledge', on_click=on_cancel_knowledge),
            width=2
        ),
        state=Knowledge.delete
    ),
    Window(
        I18NFormat('text_approve_delete'),
        Button(I18NFormat('command_knowledge_add_kb'), id='knowledge_add', on_click=to_add_file),
        Cancel(I18NFormat('close_kb'), id='cancel_knowledge', on_click=on_cancel_knowledge),
        state=Knowledge.delete_approve
    )
)