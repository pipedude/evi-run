from sqlalchemy.ext.asyncio import async_sessionmaker

from database.repositories.utils import UtilsRepository
from database.models import async_session
from config import TYPE_USAGE


async def add_daily_tokens(async_session: async_sessionmaker):
    if TYPE_USAGE != 'private':
        async with async_session() as session_:
            utils_repo = UtilsRepository(session_)
            await utils_repo.update_tokens_daily()

