import httpx
import json
import re
from ..config import settings
from ..schemas import ParsedTask, PriorityEnum
from .proxy_client import build_groq_client

# Системный промпт для Groq
SYSTEM_PROMPT = """Ты — AI помощник project-менеджера. Анализируешь сообщения в рабочем чате команды.

Твоя задача: определить, содержит ли сообщение задачу, и если да — извлечь её данные.

Признаки задачи в сообщении:
- Глаголы: "нужно", "надо", "сделай", "исправь", "добавь", "напиши", "реализуй", "проверь"
- Упоминание бага, ошибки, проблемы
- Дедлайн: "до пятницы", "до конца недели", "срочно"
- Обращение к конкретному человеку с просьбой

НЕ является задачей:
- Вопросы без конкретного действия
- Общие обсуждения
- Приветствия и светские разговоры

Отвечай ТОЛЬКО валидным JSON, без объяснений и markdown:
{
  "is_task": true или false,
  "title": "краткое название задачи (до 80 символов)",
  "assignee": "имя исполнителя или пустая строка",
  "priority": "high", "medium" или "low",
  "tag": "bug", "feat", "design", "backend" или "ai",
  "confidence": число от 0.0 до 1.0
}

Правила приоритета:
- high: слова "срочно", "критично", "продакшн упал", "блокирует", дедлайн сегодня-завтра
- low: "когда-нибудь", "не срочно", "по возможности"
- medium: всё остальное"""


async def parse_message(text: str) -> ParsedTask:
    async with build_groq_client() as client:          # ← было: httpx.AsyncClient(...)
        response = await client.post(
            "/openai/v1/chat/completions",             # ← путь без домена
            json={
                "model":    settings.GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": text},
                ],
                "max_tokens":  300,
                "temperature": 0.1,
            },
        )
        response.raise_for_status()

    data = response.json()
    raw = data["choices"][0]["message"]["content"].strip()

    # Очищаем от возможных markdown-оберток
    raw = re.sub(r"```json\s*|\s*```", "", raw).strip()

    parsed = json.loads(raw)
    return ParsedTask(**parsed)


async def summarize_tasks(tasks: list[dict]) -> str:
    async with build_groq_client() as client:          # ← то же самое
        response = await client.post(
            "/openai/v1/chat/completions",
            json={
                "model":    settings.GROQ_MODEL,
                "messages": [...],
                "max_tokens":  400,
                "temperature": 0.4,
            },
        )

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
            json={
                "model": settings.GROQ_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": f"""Составь краткий дайджест задач команды на сегодня.
Пиши на русском, кратко и по делу. Выдели: что срочно, что в работе, что нужно внимание.

Задачи:
{tasks_text}

Формат: 3-5 предложений, без списков.""",
                    }
                ],
                "max_tokens": 400,
                "temperature": 0.4,
            },
        )

    data = response.json()
    return data["choices"][0]["message"]["content"]