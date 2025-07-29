import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_dialog import setup_dialogs
from solana.rpc.async_api import AsyncClient
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from redis_service.connect import redis
from I18N.factory import i18n_factory
from bot.middlewares.database_session import DbSessionMiddleware
from bot.middlewares.translator_hub import TranslatorRunnerMiddleware
from bot.middlewares.first_time import FirstTimeMiddleware
from bot.routers.admin import router as admin_router
from bot.routers.user import router as user_router
from database.models import async_session, create_tables
from bot.dialogs.menu import dialog as menu_dialog
from bot.dialogs.knowledge import dialog as knowledge_dialog
from bot.dialogs.settings import dialog as settings_dialog
from bot.dialogs.wallet import dialog as wallet_dialog
from bot.dialogs.balance import dialog as balance_dialog
from bot.utils.check_burn_address import add_burn_address
from bot.commands import set_commands
from bot.scheduler_funcs.daily_tokens import add_daily_tokens
from bot.agents_tools.mcp_servers import get_dexpapirka_server

load_dotenv()

storage = RedisStorage(redis, key_builder=DefaultKeyBuilder(with_destiny=True))
bot = Bot(os.getenv('TELEGRAM_BOT_TOKEN'), default=DefaultBotProperties(parse_mode='HTML',
                                                                        link_preview_is_disabled=True))

dp = Dispatcher(storage=storage)

solana_client = AsyncClient("https://api.mainnet-beta.solana.com")


async def main():
    await set_commands(bot)
    print(await bot.get_me())

    scheduler = AsyncIOScheduler(timezone='UTC')
    scheduler.add_job(add_daily_tokens, trigger='cron', hour='0', minute='0', args=[async_session])
    scheduler.start()

    dexpaprika_server = await get_dexpapirka_server()

    dp.startup.register(on_startup)
    await bot.delete_webhook(drop_pending_updates=True)

    dp.include_routers(admin_router, user_router, menu_dialog, knowledge_dialog, settings_dialog, wallet_dialog, balance_dialog)

    dp.update.outer_middleware.register(DbSessionMiddleware(session_pool=async_session))
    dp.update.outer_middleware.register(TranslatorRunnerMiddleware())
    dp.update.outer_middleware.register(FirstTimeMiddleware())

    setup_dialogs(dp)

    await dp.start_polling(bot, _translator_hub=i18n_factory(), redis=redis, solana_client=solana_client, mcp_server=dexpaprika_server)


async def on_startup():
    await create_tables()
    await add_burn_address(bot=bot)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())