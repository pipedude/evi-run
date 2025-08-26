from apscheduler.schedulers.asyncio import AsyncIOScheduler

_scheduler: AsyncIOScheduler | None = None


def set_scheduler(s: AsyncIOScheduler) -> None:
    global _scheduler
    _scheduler = s


def get_scheduler() -> AsyncIOScheduler:
    if _scheduler is None:
        raise RuntimeError("Scheduler is not initialized")
    return _scheduler