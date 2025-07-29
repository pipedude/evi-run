import base64, json, uuid
import os
from io import BytesIO
from typing import Optional

import aiofiles
from agents.mcp import MCPServerStdio
from aiogram import Bot
from aiogram.types import BufferedInputFile
from redis.asyncio.client import Redis
from agents import Runner, RunConfig
from dataclasses import dataclass

from bot.agents_tools.agents_ import client, create_main_agent, memory_creator_agent
from database.models import User
from database.repositories.user import UserRepository
from database.repositories.utils import UtilsRepository
from config import ADMIN_ID


@dataclass
class AnswerText:
    answer: str
    image_bytes: Optional[bytes]
    input_tokens: int
    input_tokens_image: int
    output_tokens: int
    output_tokens_image: int

@dataclass
class AnswerImage:
    answer: str
    input_tokens: int
    output_tokens: int
    image_path: str


async def return_vectors(user_id: int, user_repo: UserRepository, utils_repo: UtilsRepository):
    memory_vector = await user_repo.get_memory_vector(user_id=user_id)
    if not memory_vector:
        vector_store = await client.vector_stores.create(name=f"user_memory_{user_id}")
        await user_repo.add_memory_vector(user_id=user_id, vector_store_id=vector_store.id)
        vector_store_id = vector_store.id
    else:
        vector_store_id = memory_vector.id_vector

    knowledge_vector = await utils_repo.get_knowledge_vectore_store_id()
    if not knowledge_vector:
        vector_store = await client.vector_stores.create(name="knowledge_base")
        await utils_repo.add_knowledge_vectore_store_id(vector_store.id)
        knowledge_id = vector_store.id
    else:
        knowledge_id = knowledge_vector.id_vector

    return vector_store_id, knowledge_id


async def encode_image(image_path):
    async with aiofiles.open(image_path, "rb") as image_file:
        return base64.b64encode(await image_file.read()).decode("utf-8")


async def text_request(text: str, user: User, user_repo: UserRepository, utils_repo: UtilsRepository,
                       redis: Redis, mcp_server_1: MCPServerStdio, bot: Bot):
    vector_store_id, knowledge_id = await return_vectors(user_id=user.telegram_id, user_repo=user_repo, utils_repo=utils_repo)
    messages = await user_repo.get_messags(user_id=user.telegram_id)
    user_wallet = await user_repo.get_wallet(user_id=user.telegram_id)

    runner = await Runner.run(
        starting_agent=await create_main_agent(user_memory_id=vector_store_id, knowledge_id=knowledge_id,
                                         mcp_server_1=mcp_server_1, user_id=user.telegram_id,
                                         private_key=user_wallet),
        input=[{'role': message.role,
                'content': message.content if f'image_{user.telegram_id}' not in message.content
                else [{"type": "input_text", "text": message.content.split('|')[-1]},
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{await encode_image(message.content.split('|')[0])}",
                }]}
               for message in messages] + [{'role': 'user', 'content': text}],

        context=(client, user.telegram_id),
        run_config=RunConfig(
            tracing_disabled=False
        )
    )

    input_tokens = 0
    output_tokens = 0
    for response in runner.raw_responses:
        input_tokens += response.usage.input_tokens
        output_tokens += response.usage.output_tokens

    # await send_raw_response(bot, str(runner.raw_responses))

    answer = runner.final_output
    is_image_answer = await redis.get(f'image_{user.telegram_id}')
    if is_image_answer:
        image_answer = json.loads(is_image_answer)
        await redis.delete(f'image_{user.telegram_id}')
        image_path = image_answer['image']
        input_tokens_image = image_answer['input_tokens']
        output_tokens_image = image_answer['output_tokens']
        # await bot.send_message(chat_id=ADMIN_ID, text=f"Image Request\n\n"
        #                                               f"Input tokens: {input_tokens_image}\n"
        #                                               f"Output tokens: {output_tokens_image}\n")

        async with aiofiles.open(image_path, "rb") as image_file:
            image_bytes = await image_file.read()
        os.remove(image_path)
        return AnswerText(answer=answer, image_bytes=image_bytes, input_tokens=input_tokens,
                          input_tokens_image=input_tokens_image, output_tokens=output_tokens, output_tokens_image=output_tokens_image)

    return AnswerText(answer=answer, image_bytes=None, input_tokens=input_tokens,
                      input_tokens_image=0, output_tokens=output_tokens, output_tokens_image=0)


async def image_request(image_bytes: bytes, user: User, user_repo: UserRepository,
                        utils_repo: UtilsRepository, redis: Redis, mcp_server_1: MCPServerStdio, bot: Bot,
                        caption: str = None):

    vector_store_id, knowledge_id = await return_vectors(user_id=user.telegram_id, user_repo=user_repo, utils_repo=utils_repo)
    messages = await user_repo.get_messags(user_id=user.telegram_id)
    user_wallet = await user_repo.get_wallet(user_id=user.telegram_id)

    id_image = uuid.uuid4()
    async with aiofiles.open(f"images/image_{user.telegram_id}_{id_image}.jpeg", "wb") as image_file:
        await image_file.write(image_bytes)

    runner = await Runner.run(
        starting_agent=await create_main_agent(user_memory_id=vector_store_id, knowledge_id=knowledge_id,
                                         mcp_server_1=mcp_server_1, user_id=user.telegram_id,
                                         private_key=user_wallet),
        input=[{'role': message.role,
                'content': message.content if f'image_{user.telegram_id}' not in message.content
                else [{"type": "input_text", "text": message.content.split('|')[-1]},
                      {
                          "type": "input_image",
                          "image_url": f"data:image/jpeg;base64,{await encode_image(message.content.split('|')[0])}",
                      }]}
               for message in messages] + [{'role': 'user', 'content': [{"type": "input_text",
                                                                         "text": f"{caption if caption else '.'}"},
                      {
                          "type": "input_image",
                          "image_url": f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode('utf-8')}",
                      }]}],

        context=(client, user.telegram_id),
        run_config=RunConfig(
            tracing_disabled=False
        )
    )

    # await send_raw_response(bot, str(runner.raw_responses))

    input_tokens = 0
    output_tokens = 0
    for response in runner.raw_responses:
        input_tokens += response.usage.input_tokens
        output_tokens += response.usage.output_tokens

    answer = runner.final_output

    return AnswerImage(answer=answer, input_tokens=input_tokens,
                       output_tokens=output_tokens, image_path=f'images/image_{user.telegram_id}_{id_image}.jpeg')


async def send_raw_response(bot: Bot, raw_response: str):
    bio = BytesIO()
    bio.write(raw_response.encode("utf-8"))
    bio.seek(0)

    await bot.send_document(
        chat_id=ADMIN_ID,
        document=BufferedInputFile(bio.read(), filename='raw_response.txt')
    )
    bio.close()