from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .database import get_session, init_db
from .models import HealthCheck, Monitor
from .schemas import HealthCheckOut, MonitorCreate, MonitorOut
from .scheduler import check_monitor, scheduler, start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    start_scheduler()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title="Uptime Monitor API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _latest_check(session: AsyncSession, monitor_id: int) -> HealthCheck | None:
    result = await session.execute(
        select(HealthCheck)
        .where(HealthCheck.monitor_id == monitor_id)
        .order_by(HealthCheck.checked_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


def _to_out(monitor: Monitor, latest: HealthCheck | None) -> MonitorOut:
    return MonitorOut(
        id=monitor.id,
        url=monitor.url,
        name=monitor.name,
        created_at=monitor.created_at,
        latest_check=HealthCheckOut.model_validate(latest) if latest else None,
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/monitors", response_model=MonitorOut, status_code=201)
async def create_monitor(
    payload: MonitorCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    monitor = Monitor(url=str(payload.url), name=payload.name)
    session.add(monitor)
    await session.commit()
    await session.refresh(monitor)
    background_tasks.add_task(check_monitor, monitor.id, monitor.url)
    return _to_out(monitor, None)


@app.get("/api/monitors", response_model=list[MonitorOut])
async def list_monitors(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Monitor).order_by(Monitor.created_at))
    monitors = result.scalars().all()
    return [_to_out(m, await _latest_check(session, m.id)) for m in monitors]


@app.get("/api/monitors/{monitor_id}/history", response_model=list[HealthCheckOut])
async def monitor_history(
    monitor_id: int, session: AsyncSession = Depends(get_session)
):
    monitor = await session.get(Monitor, monitor_id)
    if monitor is None:
        raise HTTPException(status_code=404, detail="Monitor not found")
    result = await session.execute(
        select(HealthCheck)
        .where(HealthCheck.monitor_id == monitor_id)
        .order_by(HealthCheck.checked_at.desc())
        .limit(settings.history_limit)
    )
    return list(result.scalars().all())


@app.delete("/api/monitors/{monitor_id}", status_code=204)
async def delete_monitor(
    monitor_id: int, session: AsyncSession = Depends(get_session)
):
    monitor = await session.get(Monitor, monitor_id)
    if monitor is None:
        raise HTTPException(status_code=404, detail="Monitor not found")
    await session.delete(monitor)
    await session.commit()
