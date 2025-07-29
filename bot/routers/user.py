import asyncio
from io import BytesIO

from redis.asyncio.client import Redis
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram_dialog import DialogManager, StartMode
from fluentogram import TranslatorHub

from database.repositories.user import UserRepository
from database.repositories.utils import UtilsRepository
from database.models import User
import bot.keyboards.inline as inline_kb
from bot.states.states import Menu, Settings, Knowledge, Wallet, Input, Balance
from bot.utils.send_answer import process_after_photo, process_after_text
from bot.utils.funcs_gpt import transcribe_audio, add_file_to_memory
from config import TYPE_USAGE, ADMIN_ID
from bot.utils.check_payment import check_payment_sol, check_payment_ton

router = Router()


DICT_FORMATS = {
    "doc": "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "md": "text/markdown",
    "pdf": "application/pdf",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    'txt': 'text/plain',
    'py': 'text/x-python'
}


@router.message(CommandStart())
async def start(message: Message, user_repo: UserRepository, state: FSMContext, user: User, i18n):
    await state.clear()
    await message.answer(text=i18n.get('start_text'),
                         reply_markup=inline_kb.close_text(i18n.get('close_kb')))


@router.callback_query(F.data.startswith('select_language_'))
async def select_language(callback: CallbackQuery, user_repo: UserRepository, user: User, i18n, _translator_hub: TranslatorHub):
    lang = callback.data.split('_')[2]
    translator = _translator_hub.get_translator_by_locale(lang)

    await user_repo.update(user, language=lang)

    await callback.message.edit_text(text=translator.get('start_text'),
                                     reply_markup=inline_kb.close_text(translator.get('close_kb')))


@router.message(Command('wallet'))
async def cmd_wallet(message: Message, state: FSMContext, dialog_manager: DialogManager):
    await state.set_state(Input.main)
    await dialog_manager.start(state=Wallet.main, mode=StartMode.RESET_STACK)


@router.message(Command('help'))
async def cmd_help(message: Message, state: FSMContext, i18n):
    await state.clear()
    await message.answer(text=i18n.get('cmd_help_text'), reply_markup=inline_kb.close_text(i18n.get('close_kb')))


@router.callback_query(F.data == 'close')
async def close(callback: CallbackQuery, utils_repo: UtilsRepository, state: FSMContext, i18n):
    await state.clear()
    await callback.message.delete()


@router.message(Command('settings'))
async def cmd_settings(message: Message, dialog_manager: DialogManager, state: FSMContext):
    await state.clear()
    await dialog_manager.start(state=Settings.main, mode=StartMode.RESET_STACK)


@router.message(Command('new'))
async def cmd_new(message: Message, dialog_manager: DialogManager, state: FSMContext):
    await state.clear()
    await dialog_manager.start(state=Menu.new, mode=StartMode.RESET_STACK)


@router.message(Command('save'))
async def cmd_save(message: Message, state: FSMContext, dialog_manager: DialogManager):
    await state.clear()
    await dialog_manager.start(state=Menu.save, mode=StartMode.RESET_STACK)


@router.message(Command('delete'))
async def cmd_delete(message: Message, state: FSMContext, dialog_manager: DialogManager):
    await state.clear()
    await dialog_manager.start(state=Menu.delete, mode=StartMode.RESET_STACK)


@router.message(Command('balance'))
async def cmd_settings(message: Message, dialog_manager: DialogManager, state: FSMContext):
    await state.clear()
    await dialog_manager.start(state=Balance.main, mode=StartMode.RESET_STACK)


@router.message(F.text, StateFilter(None))
async def text_input(message: Message, user_repo: UserRepository, utils_repo: UtilsRepository, redis: Redis, user: User, i18n, mcp_server):
    if await redis.get(f'request_{message.from_user.id}'):
        return
    if TYPE_USAGE == 'private':
        if message.from_user.id != ADMIN_ID:
            return
    else:
        if user.balance_credits <= 0:
            return await message.answer(i18n.get('warning_text_no_credits'))

    await redis.set(f'request_{message.from_user.id}', 't', ex=40)
    mess_to_delete = await message.answer(text=i18n.get('wait_answer_text'))
    task = asyncio.create_task(process_after_text(message=message, user=user, user_repo=user_repo, utils_repo=utils_repo,
                                                  redis=redis, i18n=i18n, mess_to_delete=mess_to_delete, mcp_server_1=mcp_server))


@router.message(F.photo, StateFilter(None))
async def photo_input(message: Message, user_repo: UserRepository, utils_repo: UserRepository, redis: Redis, user: User, i18n, mcp_server):
    if await redis.get(f'request_{message.from_user.id}'):
        return
    if TYPE_USAGE == 'private':
        if message.from_user.id != ADMIN_ID:
            return
    else:
        if user.balance_credits <= 0:
            return await message.answer(i18n.get('warning_text_no_credits'))

    await redis.set(f'request_{message.from_user.id}', 't', ex=40)
    mess_to_delete = await message.answer(text=i18n.get('wait_answer_text'))
    task = asyncio.create_task(process_after_photo(message=message, user=user, user_repo=user_repo, utils_repo=utils_repo,
                                                   redis=redis, i18n=i18n, mess_to_delete=mess_to_delete, mcp_server_1=mcp_server))


@router.message(F.voice, StateFilter(None))
async def input_voice(message: Message, user_repo: UserRepository, utils_repo: UserRepository, redis: Redis, user: User, i18n, mcp_server):
    if await redis.get(f'request_{message.from_user.id}'):
        return
    if TYPE_USAGE == 'private':
        if message.from_user.id != ADMIN_ID:
            return
    else:
        if user.balance_credits <= 0:
            return await message.answer(i18n.get('warning_text_no_credits'))

    await redis.set(f'request_{message.from_user.id}', 't', ex=40)
    mess_to_delete = await message.answer(text=i18n.get('wait_answer_text'))
    voice_id = message.voice.file_id
    file_path = await message.bot.get_file(file_id=voice_id)
    file_bytes = (await message.bot.download_file(file_path.file_path)).read()
    try:
        text_from_voice = await transcribe_audio(bytes_audio=file_bytes)
    except Exception as e:
        await message.answer(text=i18n.get('warning_text_error'))
        await redis.delete(f'request_{message.from_user.id}')
        return await mess_to_delete.delete()

    task = asyncio.create_task(
        process_after_text(message=message, user=user, user_repo=user_repo, utils_repo=utils_repo,
                           redis=redis, i18n=i18n, mess_to_delete=mess_to_delete, text_from_voice=text_from_voice, mcp_server_1=mcp_server))


@router.message(F.document, StateFilter(None))
async def input_document(message: Message, user_repo: UserRepository, utils_repo: UserRepository, redis: Redis, user: User, i18n):
    if await redis.get(f'request_{message.from_user.id}'):
        return
    if TYPE_USAGE == 'private':
        if message.from_user.id != ADMIN_ID:
            return
    else:
        if user.balance_credits <= 0:
            return await message.answer(i18n.get('warning_text_no_credits'))

    format_doc = message.document.file_name.split('.')[-1]
    if format_doc not in DICT_FORMATS:
        return await message.answer(i18n.get('warning_text_format'))

    await redis.set(f'request_{message.from_user.id}', 't', ex=40)
    mess_to_delete = await message.answer(text=i18n.get('wait_answer_text'))
    file_id = message.document.file_id
    file_path = await message.bot.get_file(file_id=file_id)
    file_bytes = (await message.bot.download_file(file_path.file_path)).read()
    try:
        await add_file_to_memory(user_repo=user_repo, user=user,
                                 file_name=message.document.file_name, file_bytes=file_bytes,
                                 mem_type=DICT_FORMATS.get(format_doc))
        await message.answer(i18n.get('text_document_upload'))
    except Exception as e:
        await message.answer(i18n.get('warning_text_error'))
    finally:
        await redis.delete(f'request_{message.from_user.id}')
        await mess_to_delete.delete()


@router.callback_query(F.data.startswith('check_payment_'))
async def check_payment(callback: CallbackQuery, user_repo: UserRepository,
                        utils_repo: UtilsRepository, user: User, solana_client, i18n):
    id_payment = int(callback.data.split('_')[-1])
    await callback.answer('')
    payment = await utils_repo.get_payment(payment_id=id_payment)
    message = await callback.message.answer(text=i18n.get('wait_check_payment_text'))
    try:
        if payment.crypto_currency == 'SOL':
            is_check = await check_payment_sol(amount=payment.crypto_amount, client=solana_client)
        else:
            is_check = await check_payment_ton(amount=payment.crypto_amount)

        if is_check:
            await user_repo.add_user_credits(user_id=user.telegram_id, balance_credits=payment.amount_usd * 1000)
            await utils_repo.update_payment_status(payment_id=payment.id, status='confirmed')
            await callback.message.delete()
            return await message.edit_text(text=i18n.get('check_payment_success_text'))
    except Exception as e:
        print(e)
        pass

    await message.edit_text(text=i18n.get('check_payment_error_text'))


@router.callback_query(F.data.startswith('markdown_'))
async def md_answer(callback: CallbackQuery, user_repo: UserRepository, user: User, i18n, bot):
    row_id = int(callback.data.split('_')[-1])

    row = await user_repo.get_row_for_md(row_id=row_id)
    if not row:
        return await callback.answer(i18n.get('warning_text_no_row_md'), show_alert=True)

    bio = BytesIO()
    bio.write(row.content.encode("utf-8"))
    bio.seek(0)

    await callback.bot.send_document(
        chat_id=callback.from_user.id,
        document=BufferedInputFile(bio.read(), filename=f'{row.id}.md')
    )
    bio.close()

