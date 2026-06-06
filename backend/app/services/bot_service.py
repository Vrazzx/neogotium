# backend/app/services/bot_service.py

import json
import os
import logging
import httpx

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters

from ..config import settings

logger = logging.getLogger(__name__)


# ─── диагностика ────────────────────────────────────────────────────────────

async def test_bot_connection() -> bool:
    if settings.CF_PROXY_URL:
        url = f"{settings.CF_PROXY_URL.rstrip('/')}/telegram/bot{settings.TELEGRAM_BOT_TOKEN}/getMe"
    else:
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getMe"

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url)
        logger.info(f"[bot test] url={url}")
        logger.info(f"[bot test] status={r.status_code} body={r.text[:200]}")
        return r.status_code == 200


# ─── хэндлеры ───────────────────────────────────────────────────────────────

def build_task_keyboard(data: dict) -> InlineKeyboardMarkup:
    payload = json.dumps(data, ensure_ascii=False)[:100]
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Добавить в канбан", callback_data=f"add:{payload}"),
        InlineKeyboardButton("❌ Игнор",             callback_data="ignore"),
    ]])


async def handle_message(update: Update, context) -> None:
    msg = update.message
    if not msg or not msg.text or msg.text.startswith("/"):
        return

    from .ai_parser import parse_message
    parsed = await parse_message(msg.text)

    if parsed.is_task and parsed.confidence > 0.6:
        text = (
            f"🤖 *AI PM обнаружил задачу*\n\n"
            f"📋 *{parsed.title}*\n"
            f"👤 Исполнитель: {parsed.assignee or 'не указан'}\n"
            f"🔥 Приоритет: {parsed.priority.value}\n"
            f"🏷 Тег: #{parsed.tag}\n"
            f"📊 Уверенность: {int(parsed.confidence * 100)}%"
        )
        await msg.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=build_task_keyboard({
                "title":    parsed.title,
                "assignee": parsed.assignee,
                "priority": parsed.priority.value,
                "tag":      parsed.tag,
                "source":   msg.text[:200],
                "chat_id":  str(msg.chat_id),
            }),
        )


async def handle_voice(update: Update, context) -> None:
    msg = update.message
    await msg.reply_text("🎙 Обрабатываю голосовое сообщение...")

    from .audio_service import download_telegram_voice, transcribe_and_extract_tasks
    from ..database import AsyncSessionLocal
    from sqlalchemy import select
    from ..models import Board

    voice_path = await download_telegram_voice(
        file_id=msg.voice.file_id,
        bot_token=settings.TELEGRAM_BOT_TOKEN,
    )
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Board).where(Board.telegram_chat_id == str(msg.chat_id))
            )
            board = result.scalar_one_or_none()
            if not board:
                await msg.reply_text("⚠️ Доска не найдена для этого чата")
                return
            tasks = await transcribe_and_extract_tasks(voice_path, board.id, db)

        if tasks:
            lines = "\n".join(f"  • {t['title']} → {t['assignee'] or '?'}" for t in tasks)
            await msg.reply_text(f"✅ Извлечено {len(tasks)} задач:\n{lines}")
        else:
            await msg.reply_text("🔍 Задач не обнаружено")
    finally:
        os.unlink(voice_path)


async def handle_callback(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "ignore":
        await query.edit_message_text("❌ Задача проигнорирована")
        return

    if query.data.startswith("add:"):
        data = json.loads(query.data[4:])
        await query.edit_message_text(
            f"✅ Задача *{data.get('title', '')}* добавлена в канбан!",
            parse_mode="Markdown",
        )


async def send_daily_digest(chat_id: str, digest_text: str) -> None:
    app = create_application()
    await app.bot.send_message(
        chat_id=chat_id,
        text=f"☀️ *Дайджест задач на сегодня*\n\n{digest_text}",
        parse_mode="Markdown",
    )


# ─── фабрика приложения ──────────────────────────────────────────────────────

def create_application() -> Application:
    builder = Application.builder().token(settings.TELEGRAM_BOT_TOKEN)

    if settings.CF_PROXY_URL:
        base = f"{settings.CF_PROXY_URL.rstrip('/')}/telegram/bot"
        base_file = f"{settings.CF_PROXY_URL.rstrip('/')}/telegram/file/bot"
        logger.info(f"[bot] using CF proxy base_url={base}")
        builder = builder.base_url(base).base_file_url(base_file)
    else:
        logger.info("[bot] no proxy, direct connection")

    app = builder.build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(CallbackQueryHandler(handle_callback))
    return app