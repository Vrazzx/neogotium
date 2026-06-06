from fastapi import APIRouter, Request, Response
from telegram import Update
from ..services.bot_service import create_application

router = APIRouter()
_app = None


def get_app():
    global _app
    if _app is None:
        _app = create_application()
    return _app


@router.post("/webhook")
async def telegram_webhook(request: Request):
    """Telegram шлёт сюда все обновления."""
    data = await request.json()
    update = Update.de_json(data, get_app().bot)
    await get_app().process_update(update)
    return Response(status_code=200)