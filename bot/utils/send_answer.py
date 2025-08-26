import re

from agents.mcp import MCPServerStdio
from aiogram.types import Message, BufferedInputFile
from chatgpt_md_converter import telegram_format
from redis.asyncio.client import Redis

from bot.utils.calculate_tokens import calculate_tokens
from database.models import User
from database.repositories.user import UserRepository
from database.repositories.utils import UtilsRepository
from bot.utils.agent_requests import AnswerText, text_request, AnswerImage, image_request
import bot.keyboards.inline as inline_kb
from config import TOKENS_LIMIT_FOR_WARNING_MESSAGE


async def send_answer_text(user_ques: str, message: Message, answer: AnswerText, user: User, user_repo: UserRepository, i18n):
    if answer.image_bytes:
        await message.answer_photo(photo=BufferedInputFile(answer.image_bytes, filename=f"{user.telegram_id}.jpeg"),
                                   caption=answer.answer)

        await user_repo.add_context(user_id=user.telegram_id, role='user', content=user_ques)
        await user_repo.add_context(user_id=user.telegram_id, role='assistant', content=answer.answer)
    else:
        await user_repo.add_context(user_id=user.telegram_id, role='user', content=user_ques)
        row_id = await user_repo.add_context(user_id=user.telegram_id, role='assistant', content=answer.answer)
        messages = split_code_message(answer.answer)

        for index, mess in enumerate(messages, 1):
            if len(messages) == index:
                await message.answer(mess,
                                     reply_markup=inline_kb.keyboard_md(row_id=row_id, text=i18n.get('answer_md')))
            else:
                await message.answer(mess)


def split_code_message(text, chunk_size=3700, type_: str = None):
    if not type_:
        text = telegram_format(text)
        text = text.replace('&lt;blockquote expandable&gt;', '<blockquote expandable>')
    chunks = []
    current_chunk = ""
    open_tags = []
    position = 0
    tag_pattern = re.compile(r"<(\/)?([a-zA-Z0-9\-]+)([^>]*)>")

    def close_open_tags():
        return "".join(f"</{tag}>" for tag in reversed(open_tags))

    def reopen_tags():
        return "".join(f"<{tag if tag != 'blockquote' else 'blockquote expandable'}>" for tag in open_tags)

    while position < len(text):
        if len(current_chunk) >= chunk_size:
            current_chunk += close_open_tags()
            chunks.append(current_chunk)
            current_chunk = reopen_tags()

        next_cut = position + chunk_size - len(current_chunk)
        next_match = tag_pattern.search(text, position, next_cut)

        if not next_match:
            current_chunk += text[position:next_cut]
            position = next_cut
        else:
            start, end = next_match.span()
            tag_full = next_match.group(0)
            is_closing = next_match.group(1) == "/"
            tag_name = next_match.group(2)

            if start - position + len(current_chunk) >= chunk_size:
                current_chunk += close_open_tags()
                chunks.append(current_chunk)
                current_chunk = reopen_tags()

            current_chunk += text[position:start]
            position = start

            if is_closing:
                if tag_name in open_tags:
                    open_tags.remove(tag_name)
            else:
                open_tags.append(tag_name)

            current_chunk += tag_full
            position = end

    if current_chunk:
        current_chunk += close_open_tags()
        chunks.append(current_chunk)

    return chunks


async def process_after_text(message: Message, user: User, user_repo: UserRepository,
                             utils_repo: UtilsRepository, redis: Redis, i18n,
                             mess_to_delete: Message, mcp_server_1: MCPServerStdio, scheduler, text_from_voice: str = None,
                             constant_text: str = None):
    try:
        if text_from_voice:
            user_ques = text_from_voice
        elif constant_text:
            user_ques = constant_text
        else:
            user_ques = message.text

        answer = await text_request(text=user_ques, user=user,
                                    user_repo=user_repo, utils_repo=utils_repo, redis=redis, mcp_server_1=mcp_server_1,
                                    bot=message.bot, scheduler=scheduler)

        await send_answer_text(user_ques=user_ques,
                               message=message, answer=answer, user=user, user_repo=user_repo, i18n=i18n)

        if answer.input_tokens + answer.output_tokens > TOKENS_LIMIT_FOR_WARNING_MESSAGE:
            await message.answer(i18n.get('warning_text_tokens'))

        await calculate_tokens(user=user, user_repo=user_repo, input_tokens_text=answer.input_tokens,
                               input_tokens_img=answer.input_tokens_image, output_tokens_text=answer.output_tokens,
                               output_tokens_img=answer.output_tokens_image)
    except Exception as e:
        print(e)
        await message.answer(text=i18n.get('warning_text_error'))
    finally:
        await redis.delete(f'request_{message.from_user.id}')
        await mess_to_delete.delete()


async def send_answer_photo(message: Message, answer: AnswerImage, user: User, user_repo: UserRepository):
    caption = message.caption if message.caption else '.'
    await user_repo.add_context(user_id=user.telegram_id, role='user', content=f'{answer.image_path}|{caption}')
    await user_repo.add_context(user_id=user.telegram_id, role='assistant', content=answer.answer)

    messages = split_code_message(answer.answer)

    for index, mess in enumerate(messages, 1):
        await message.answer(mess)


async def process_after_photo(message: Message, user: User, user_repo: UserRepository,
                              utils_repo: UtilsRepository, redis: Redis, i18n, mess_to_delete: Message,
                              mcp_server_1: MCPServerStdio, scheduler):
    try:
        file_id = message.photo[-1].file_id
        file_path = await message.bot.get_file(file_id=file_id)
        file_bytes = (await message.bot.download_file(file_path.file_path)).read()
        answer = await image_request(image_bytes=file_bytes, user=user, user_repo=user_repo,
                                     utils_repo=utils_repo, redis=redis, mcp_server_1=mcp_server_1, bot=message.bot,
                                     caption=message.caption, scheduler=scheduler)

        await send_answer_photo(message=message, answer=answer, user=user, user_repo=user_repo)

        if answer.input_tokens + answer.output_tokens > TOKENS_LIMIT_FOR_WARNING_MESSAGE:
            await message.answer(i18n.get('warning_text_tokens'))

        await calculate_tokens(user=user, user_repo=user_repo, input_tokens_text=answer.input_tokens,
                               input_tokens_img=0, output_tokens_text=answer.output_tokens,
                               output_tokens_img=0)
    except Exception as e:
        await message.answer(text=i18n.get('warning_text_error'))
    finally:
        await redis.delete(f'request_{message.from_user.id}')
        await mess_to_delete.delete()