import asyncio

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from .checker import CheckResult, check_url
from .config import settings
from .database import SessionLocal
from .models import HealthCheck, Monitor

scheduler = AsyncIOScheduler()


def _record(session, monitor_id: int, result: CheckResult) -> None:
    session.add(
        HealthCheck(
            monitor_id=monitor_id,
            status_code=result.status_code,
            response_time_ms=result.response_time_ms,
            is_up=result.is_up,
            error=result.error,
        )
    )


async def check_monitor(monitor_id: int, url: str) -> None:
    """Check one monitor and store the result (used for the immediate check)."""
    timeout = httpx.Timeout(settings.request_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        result = await check_url(client, url)
    async with SessionLocal() as session:
        _record(session, monitor_id, result)
        await session.commit()


async def check_all_monitors() -> None:
    """Ping every registered monitor concurrently and persist the results."""
    async with SessionLocal() as session:
        monitors = (await session.execute(select(Monitor))).scalars().all()
        targets = [(m.id, m.url) for m in monitors]

    if not targets:
        return

    timeout = httpx.Timeout(settings.request_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        results = await asyncio.gather(*(check_url(client, url) for _, url in targets))

    async with SessionLocal() as session:
        for (monitor_id, _), result in zip(targets, results):
            _record(session, monitor_id, result)
        await session.commit()


def start_scheduler() -> None:
    scheduler.add_job(
        check_all_monitors,
        "interval",
        seconds=settings.check_interval_seconds,
        id="check_all_monitors",
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
