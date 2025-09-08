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


def split_code_message(text, type_: str = None):
    """
    Reliably split Telegram HTML into chunks while preserving valid markup.
    - Self-closing tags are not pushed to the stack and therefore are not closed.
    - For opened tags we store the full opening form including attributes to re-open later.
    - Never split inside an HTML tag or inside an HTML entity.
    - Preserve Telegram-specific nuances such as <blockquote expandable> and <pre>/<code> blocks.
    """
    if not type_:
        text = telegram_format(text)
        text = text.replace('&lt;blockquote expandable&gt;', '<blockquote expandable>')

    # Escape HTML comments <!-- ... --> so they are treated as text,
    # not as tags that could break the open/close stack while splitting
    comment_pattern = re.compile(r"<!--.*?-->", re.DOTALL)

    def _escape_comment(m):
        c = m.group(0)
        return c.replace('<', '&lt;').replace('>', '&gt;')

    text = comment_pattern.sub(_escape_comment, text)

    chunks = []
    current_chunk = ""

    # Stack of opened tags: items are dicts {name, open}
    open_stack = []
    position = 0

    tag_pattern = re.compile(r"<(\/)?([a-zA-Z0-9\-]+)([^>]*)>")

    # Set of self-closing/non-closing tags in Telegram HTML context
    SELF_CLOSING = {"br"}

    def is_self_closing(tag_name: str, tag_full: str) -> bool:
        return tag_name in SELF_CLOSING or tag_full.strip().endswith('/>')

    def close_open_tags() -> str:
        # Close only normal opened tags in reverse order
        closing = []
        for item in reversed(open_stack):
            closing.append(f"</{item['name']}>")
        return "".join(closing)

    def reopen_tags() -> str:
        # Re-open saved opening tags (with attributes) in original order.
        # For blockquote expandable we keep the original form as-is.
        return "".join(item['open'] for item in open_stack)

    def escape_tag_text(tag_text: str) -> str:
        """Render a tag as plain text by escaping angle brackets."""
        return tag_text.replace('<', '&lt;').replace('>', '&gt;')

    def safe_cut_index(text_: str, start: int, tentative_end: int) -> int:
        """Shift a split position so that we never cut inside a tag or an HTML entity."""
        end = min(tentative_end, len(text_))
        if end <= start:
            return end

        segment = text_[start:end]

        # 1) Do not split inside a tag: if the last '<' is after the last '>' -> move back to that '<'
        last_lt = segment.rfind('<')
        last_gt = segment.rfind('>')
        if last_lt != -1 and (last_gt == -1 or last_lt > last_gt):
            end = start + last_lt
            if end <= start:
                return start
            segment = text_[start:end]

        # 2) Do not split inside an entity: if there's '&' after the last ';' -> move back to that '&'
        last_amp = segment.rfind('&')
        last_semi = segment.rfind(';')
        if last_amp != -1 and (last_semi == -1 or last_amp > last_semi):
            end = start + last_amp

        return end

    text_len = len(text)
    while position < text_len:
        # Dynamic budget for the current chunk
        SAFETY = 64
        BASE_LIMIT = 3900
        allowed_total = BASE_LIMIT - len(close_open_tags()) - len(reopen_tags()) - SAFETY
        # Clamp to reasonable bounds just in case
        if allowed_total < 1000:
            allowed_total = 1000
        elif allowed_total > BASE_LIMIT:
            allowed_total = BASE_LIMIT

        # If current chunk is full — close and start a new one
        if len(current_chunk) >= allowed_total:
            current_chunk += close_open_tags()
            chunks.append(current_chunk)
            current_chunk = reopen_tags()

        # Compute the boundary where we can safely write more characters
        tentative_end = position + (allowed_total - len(current_chunk))
        if tentative_end <= position:
            # No room left — force a chunk break
            current_chunk += close_open_tags()
            chunks.append(current_chunk)
            current_chunk = reopen_tags()
            continue

        # Look for the next tag before the boundary
        next_match = tag_pattern.search(text, position, min(tentative_end, text_len))

        if not next_match:
            # No tags before boundary — split at a safe position
            cut_idx = safe_cut_index(text, position, min(tentative_end, text_len))
            if cut_idx == position:
                # No safe position found in the window — extend the window to find the next tag/entity end
                extend_end = min(position + 100 + (allowed_total - len(current_chunk)), text_len)
                next_match_ext = tag_pattern.search(text, position, extend_end)
                if next_match_ext:
                    cut_idx = next_match_ext.start()
                else:
                    # No complete tag found in lookahead — split before a partial '<...'
                    extended_segment = text[position:extend_end]
                    last_lt = extended_segment.rfind('<')
                    if last_lt != -1:
                        # Check if there's '>' after that '<' in the extended window
                        gt_after = extended_segment.find('>', last_lt + 1)
                        if gt_after == -1:
                            # Tag is not completed within the window — cut before '<'
                            cut_idx = position + last_lt
                        else:
                            cut_idx = extend_end
                    else:
                        cut_idx = extend_end
            # Zero-shift guard (when cut_idx == position):
            # happens if a partial tag starts exactly at 'position'.
            if cut_idx == position:
                if current_chunk:
                    # Close current chunk and start a new one before continuing
                    current_chunk += close_open_tags()
                    chunks.append(current_chunk)
                    current_chunk = reopen_tags()
                    continue
                else:
                    # Current chunk is empty — extend search forward to the next '>' and advance at least to it
                    search_end = min(position + 300, text_len)
                    gt_global = text.find('>', position, search_end)
                    if gt_global != -1:
                        cut_idx = gt_global + 1
                    else:
                        # Last resort — move to search_end to avoid infinite loop
                        cut_idx = search_end
            current_chunk += text[position:cut_idx]
            position = cut_idx
            continue

        # There is a tag before the boundary
        start_tag, end_tag = next_match.span()
        tag_full = next_match.group(0)
        is_closing = next_match.group(1) == "/"
        tag_name = next_match.group(2)
        _ = next_match.group(3)

        # If text before the tag doesn't fit — break the chunk
        if (start_tag - position) + len(current_chunk) > allowed_total:
            current_chunk += close_open_tags()
            chunks.append(current_chunk)
            current_chunk = reopen_tags()
            continue

        # Append text up to the tag
        current_chunk += text[position:start_tag]
        position = start_tag

        # Tag handling
        if is_closing:
            # Prefer strict LIFO, but outside pre/code try to fix nesting to preserve formatting
            if open_stack and open_stack[-1]['name'] == tag_name:
                # Does the tag itself fit into the current chunk?
                if len(current_chunk) + (end_tag - start_tag) > allowed_total:
                    current_chunk += close_open_tags()
                    chunks.append(current_chunk)
                    current_chunk = reopen_tags()
                current_chunk += tag_full
                # Pop the top tag
                open_stack.pop()
            else:
                if open_stack and open_stack[-1]['name'] in {"pre", "code"}:
                    # Inside pre/code escape foreign closing tags as text
                    escaped = escape_tag_text(tag_full)
                    if len(current_chunk) + len(escaped) > allowed_total:
                        current_chunk += close_open_tags()
                        chunks.append(current_chunk)
                        current_chunk = reopen_tags()
                    current_chunk += escaped
                else:
                    # Outside pre/code: normalize nesting by auto-closing tags down to target.
                    # Find the target tag in the stack (from the end). If not found — escape as text.
                    target_idx = None
                    for idx in range(len(open_stack) - 1, -1, -1):
                        if open_stack[idx]['name'] == tag_name:
                            target_idx = idx
                            break
                    if target_idx is None:
                        escaped = escape_tag_text(tag_full)
                        if len(current_chunk) + len(escaped) > allowed_total:
                            current_chunk += close_open_tags()
                            chunks.append(current_chunk)
                            current_chunk = reopen_tags()
                        current_chunk += escaped
                    else:
                        # Close all tags above the target sequentially
                        names_above = [open_stack[i]['name'] for i in range(len(open_stack) - 1, target_idx, -1)]
                        estimated = sum(len(f"</{n}>") for n in names_above) + (end_tag - start_tag)
                        if len(current_chunk) + estimated > allowed_total:
                            # Start a new chunk before emitting the closing sequence to stay within budget
                            current_chunk += close_open_tags()
                            chunks.append(current_chunk)
                            current_chunk = reopen_tags()
                        # Emit the closing tags for the ones above the target
                        for n in names_above:
                            current_chunk += f"</{n}>"
                            open_stack.pop()
                        # Finally append the original closing tag for the target and pop it
                        current_chunk += tag_full
                        open_stack.pop()  # снимаем целевой тег
        else:
            # Opening tag
            # If we are inside pre/code and encounter a non pre/code tag — escape as text, do not push to stack
            if open_stack and open_stack[-1]['name'] in {"pre", "code"} and tag_name not in {"pre", "code"}:
                escaped_open = escape_tag_text(tag_full)
                if len(current_chunk) + len(escaped_open) > allowed_total:
                    current_chunk += close_open_tags()
                    chunks.append(current_chunk)
                    current_chunk = reopen_tags()
                current_chunk += escaped_open
            else:
                if len(current_chunk) + (end_tag - start_tag) > allowed_total:
                    current_chunk += close_open_tags()
                    chunks.append(current_chunk)
                    current_chunk = reopen_tags()

                current_chunk += tag_full

                # Do not push self-closing tags to the stack
                if not is_self_closing(tag_name, tag_full):
                    # Save the original opening form with attributes.
                    # Special case blockquote expandable — keep as-is.
                    opening = tag_full
                    open_stack.append({
                        'name': tag_name,
                        'open': opening,
                    })

        position = end_tag

    # Finalization
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