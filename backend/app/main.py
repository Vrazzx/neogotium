from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import tasks, webhook
from .routers import boards as boards_router
from .config import settings
import asyncio
import logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаём таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Создаём доску по умолчанию если её нет
    from .database import AsyncSessionLocal
    from sqlalchemy import select
    from .models import Board
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Board).where(Board.id == 1))
        if not result.scalar_one_or_none():
            db.add(Board(name="Основная доска"))
            await db.commit()
            logger.info("Created default board")

    # Запускаем Telegram бота
    bot_task = None
    if settings.TELEGRAM_BOT_TOKEN:
        try:
            from .services.bot_service import test_bot_connection, create_application
            
            ok = await test_bot_connection()
            logger.info(f"Direct connection test: {'OK' if ok else 'FAILED'}")

            tg_app = create_application()
            await tg_app.initialize()

            if settings.TELEGRAM_WEBHOOK_URL:
                await tg_app.bot.set_webhook(
                    url=f"{settings.TELEGRAM_WEBHOOK_URL}/webhook"
                )
                await tg_app.start()
                logger.info("Telegram bot started via webhook")
            else:
                await tg_app.start()
                await tg_app.updater.start_polling(drop_pending_updates=True)
                logger.info("Telegram bot started via polling")

                async def _keep_alive():
                    try:
                        await asyncio.Event().wait()
                    except asyncio.CancelledError:
                        pass

                bot_task = asyncio.create_task(_keep_alive())
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")

    yield

    if bot_task:
        bot_task.cancel()
    await engine.dispose()


app = FastAPI(title="AI PM Bot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(boards_router.router)
app.include_router(tasks.router)
app.include_router(webhook.router)