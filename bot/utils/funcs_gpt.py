import os
from io import BytesIO

from agents import Runner, RunConfig

from bot.agents_tools.agents_ import client, create_main_agent, memory_creator_agent
from database.models import User
from database.repositories.user import UserRepository
from database.repositories.utils import UtilsRepository


async def file_to_context(utils_repo: UtilsRepository, file_name: str, file_bytes: bytes, mem_type: str):
    vector_store_id = (await utils_repo.get_knowledge_vectore_store_id())

    if not vector_store_id:
        vector_store = await client.vector_stores.create(name="knowledge_base")
        await utils_repo.add_knowledge_vectore_store_id(vector_store.id)
        vector_store_id = vector_store.id
    else:
        vector_store_id = vector_store_id.id_vector

    file = await client.files.create(
        file=(file_name, file_bytes, mem_type),
        purpose="assistants"
    )

    await client.vector_stores.files.create(
        vector_store_id=vector_store_id,
        file_id=file.id
    )

    while True:
        async for file_ in client.vector_stores.files.list(
            vector_store_id=vector_store_id,
            order='desc'
        ):
            if file_.id == file.id and file_.status == 'completed':
                return True
            if file_.id == file.id and file_.status == 'failed':
                return False


async def delete_knowledge_base(utils_repo: UtilsRepository):
    is_vector_store = (await utils_repo.get_knowledge_vectore_store_id())
    if is_vector_store:
        vector_store_id = is_vector_store.id_vector
    else:
        return

    await client.vector_stores.delete(vector_store_id=vector_store_id)

    vector_store = await client.vector_stores.create(name="knowledge_base")
    await utils_repo.delete_knowledge_vectore_store_id()
    await utils_repo.add_knowledge_vectore_store_id(vector_store.id)


async def save_user_context_txt_file(user_repo: UserRepository, user: User):
    messages = await user_repo.get_messags(user_id=user.telegram_id)
    runner = await Runner.run(
        starting_agent=memory_creator_agent,
        input=[{'role': message.role, 'content': message.content} for message in messages],
        run_config=RunConfig(
            tracing_disabled=False
        )
    )

    input_tokens = runner.raw_responses[0].usage.input_tokens
    output_tokens = runner.raw_responses[0].usage.output_tokens

    answer = runner.final_output
    byte_buffer = BytesIO(answer.encode("utf-8"))

    memory_vector = await user_repo.get_memory_vector(user_id=user.telegram_id)
    if not memory_vector:
        vector_store = await client.vector_stores.create(name=f"user_memory_{user.telegram_id}")
        await user_repo.add_memory_vector(user_id=user.telegram_id, vector_store_id=vector_store.id)
        vector_store_id = vector_store.id
    else:
        vector_store_id = memory_vector.id_vector

    file = await client.files.create(
        file=(f'context_{user.telegram_id}.txt', byte_buffer, 'text/plain'),
        purpose="assistants"
    )

    await client.vector_stores.files.create(
        vector_store_id=vector_store_id,
        file_id=file.id
    )

    while True:
        async for file_ in client.vector_stores.files.list(
                vector_store_id=vector_store_id,
                order='desc'
        ):
            if file_.id == file.id and file_.status == 'completed':
                return input_tokens, output_tokens
            if file_.id == file.id and file_.status == 'failed':
                return False


async def delete_user_memory(user_repo: UserRepository, user: User):
    memory_vector = await user_repo.get_memory_vector(user_id=user.telegram_id)
    if memory_vector:
        await client.vector_stores.delete(vector_store_id=memory_vector.id_vector)
        await user_repo.delete_memory_vector(user_id=user.telegram_id)

    images = os.listdir('images')
    for image in images:
        if str(user.telegram_id) in image:
            os.remove(f'images/{image}')


async def create_vectore_store(user_repo: UserRepository, user: User):
    vector_store = await client.vector_stores.create(name=f"user_memory_{user.telegram_id}")
    await user_repo.add_memory_vector(user_id=user.telegram_id, vector_store_id=vector_store.id)


async def transcribe_audio(bytes_audio: bytes):
    res = await client.audio.transcriptions.create(
        file=('audio.ogg', bytes_audio),
        model='whisper-1'
    )

    return res.text


async def add_file_to_memory(user_repo: UserRepository, user: User, file_name: str, file_bytes: bytes, mem_type: str):
    vector_store = await user_repo.get_memory_vector(user_id=user.telegram_id)

    if not vector_store:
        vector_store = await client.vector_stores.create(name=f"user_memory_{user.telegram_id}")
        await user_repo.add_memory_vector(user_id=user.telegram_id, vector_store_id=vector_store.id)
        vector_store_id = vector_store.id
    else:
        vector_store_id = vector_store.id_vector

    file = await client.files.create(
        file=(file_name, file_bytes, mem_type),
        purpose="assistants"
    )

    await client.vector_stores.files.create(
        vector_store_id=vector_store_id,
        file_id=file.id
    )

    while True:
        async for file_ in client.vector_stores.files.list(
                vector_store_id=vector_store_id,
                order='desc'
        ):
            if file_.id == file.id and file_.status == 'completed':
                return True
            if file_.id == file.id and file_.status == 'failed':
                return False