import os
import asyncio
import tempfile
from pathlib import Path

import httpx
from ..config import settings
from .ai_parser import parse_message
from .task_service import TaskService

# Загружаем модель один раз при старте сервера
# "base" — быстрая, русский язык поддерживается
# "small" — точнее, но медленнее (~500MB)
# "medium" — оптимально для русского
_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        model_name = os.getenv("WHISPER_MODEL", "base")
        _whisper_model = whisper.load_model(model_name)
    return _whisper_model





async def transcribe_audio(audio_path: str) -> str:
    """
    Транскрибирует аудиофайл через Whisper.
    Возвращает текст расшифровки.
    Запускает CPU-тяжёлую задачу в отдельном потоке через run_in_executor.
    """
    loop = asyncio.get_event_loop()

    def _transcribe():
        model = get_whisper_model()
        result = model.transcribe(
            audio_path,
            language="ru",          # принудительно русский для скорости
            task="transcribe",      # "translate" для перевода на английский
            fp16=False,             # False если нет GPU
            verbose=False,
        )
        return result["text"].strip()

    text = await loop.run_in_executor(None, _transcribe)
    return text


async def transcribe_and_extract_tasks(
    audio_path: str,
    board_id: int,
    db,
) -> list[dict]:
    """
    Полный pipeline: аудио → текст → задачи → запись в БД.
    Возвращает список созданных задач.
    """
    # 1. Транскрибируем
    full_text = await transcribe_audio(audio_path)

    if not full_text:
        return []

    # 2. Разбиваем на предложения (простой сплит по знакам препинания)
    import re
    sentences = re.split(r'[.!?]\s+', full_text)

    # 3. Анализируем каждое предложение на задачу
    created_tasks = []
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 10:     # слишком короткие пропускаем
            continue

        parsed = await parse_message(sentence)

        if parsed.is_task and parsed.confidence > 0.65:
            task = await TaskService.create_from_parsed(
                db=db,
                board_id=board_id,
                parsed=parsed,
                source_message=f"[Аудио] {sentence}",
            )
            created_tasks.append({
                "id": task.id,
                "title": task.title,
                "assignee": task.assignee,
                "priority": task.priority.value,
            })

    return created_tasks


async def download_telegram_voice(file_id: str, bot_token: str) -> str:
    from .proxy_client import build_telegram_client

    async with build_telegram_client() as client:
        # getFile — путь /botTOKEN/getFile
        r = await client.get(
            f"/bot{bot_token}/getFile",
            params={"file_id": file_id},
        )
        file_path = r.json()["result"]["file_path"]

        # Файл скачивается с другого хоста — api.telegram.org/file/
        # CF Worker должен также проксировать /telegram-files/ → https://api.telegram.org/file/
        r = await client.get(f"/file/bot{bot_token}/{file_path}")

    suffix = Path(file_path).suffix or ".ogg"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(r.content)
    tmp.close()
    return tmp.name