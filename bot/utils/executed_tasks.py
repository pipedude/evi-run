import asyncio
from datetime import datetime

from agents import set_tracing_disabled

from bot.utils.create_bot import bot
from database.models import async_session
from database.repositories.user import UserRepository
from database.repositories.utils import UtilsRepository
from redis_service.connect import redis
from I18N.factory import i18n_factory
from bot.agents_tools.mcp_servers import get_dexpapirka_server
from bot.utils.scheduler_provider import get_scheduler

set_tracing_disabled(False)
CONCURRENCY_LIMIT = 10
sem = asyncio.Semaphore(CONCURRENCY_LIMIT)

translator_hub = i18n_factory()


async def execute_task(user_id: int, task_id: int):
    from bot.utils.send_answer import process_after_text

    scheduler = get_scheduler()
    async with sem:
        async with async_session() as session:
            user_repository = UserRepository(session)
            utils_repo = UtilsRepository(session)
            user = await user_repository.get_by_telegram_id(user_id)
            user_task = await user_repository.get_task(user_id=user_id, task_id=task_id)
            i18n = translator_hub.get_translator_by_locale(user.language)
            mess_to_delete = await bot.send_message(chat_id=user_id, text=i18n.get('wait_answer_text_scheduler'))
            mcp_server = await get_dexpapirka_server()

            await process_after_text(message=mess_to_delete, user=user, user_repo=user_repository, utils_repo=utils_repo,
                                     redis=redis, i18n=i18n, mess_to_delete=mess_to_delete, mcp_server_1=mcp_server,
                                     constant_text=f'<msg from Task Scheduler> {user_task.agent_message}',
                                     scheduler=scheduler)
            if user_task.schedule_type == 'once':
                await user_repository.update_task(user_id=user_id, task_id=task_id, last_executed=datetime.now(),
                                                  is_active=False)
            else:
                await user_repository.update_task(user_id=user_id, task_id=task_id, last_executed=datetime.now())
