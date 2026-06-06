# backend/app/workers/celery_app.py

import os
import asyncio
from celery import Celery
from celery.schedules import crontab

# Читаем только REDIS_URL здесь — остальное внутри тасков
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery = Celery("ai-pm", broker=REDIS_URL, backend=REDIS_URL)
celery.conf.broker_connection_retry_on_startup = True
celery.conf.timezone = "Europe/Moscow"

celery.conf.beat_schedule = {
    "daily-digest": {
        "task": "app.workers.celery_app.send_digest",
        "schedule": crontab(hour=9, minute=0),
    },
    "overdue-reminders": {
        "task": "app.workers.celery_app.check_overdue",
        "schedule": crontab(minute=0),
    },
}


@celery.task
def send_digest():
    from ..config import settings          # импорт ВНУТРИ таска
    from ..database import AsyncSessionLocal
    from ..models import Task, Board, StatusEnum
    from ..services.ai_parser import summarize_tasks
    from ..services.bot_service import send_daily_digest
    from sqlalchemy import select

    async def _run():
        async with AsyncSessionLocal() as db:
            boards = (await db.execute(select(Board))).scalars().all()
            for board in boards:
                if not board.telegram_chat_id:
                    continue
                tasks = (
                    await db.execute(
                        select(Task)
                        .where(Task.board_id == board.id)
                        .where(Task.status != StatusEnum.done)
                    )
                ).scalars().all()
                if not tasks:
                    continue
                tasks_data = [
                    {
                        "title": t.title,
                        "priority": t.priority.value,
                        "assignee": t.assignee,
                        "status": t.status.value,
                    }
                    for t in tasks
                ]
                digest = await summarize_tasks(tasks_data)
                await send_daily_digest(board.telegram_chat_id, digest)

    asyncio.run(_run())


@celery.task
def check_overdue():
    from ..database import AsyncSessionLocal
    from ..models import Task, StatusEnum
    from sqlalchemy import select
    from datetime import datetime

    async def _run():
        async with AsyncSessionLocal() as db:
            now = datetime.utcnow()
            overdue = (
                await db.execute(
                    select(Task)
                    .where(Task.due_date < now)
                    .where(Task.status != StatusEnum.done)
                )
            ).scalars().all()
            # TODO: отправить уведомления
            for task in overdue:
                print(f"Overdue: {task.title}")

    asyncio.run(_run())