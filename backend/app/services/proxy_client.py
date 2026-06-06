"""
Единственный файл для работы с Cloudflare Worker прокси.
Все запросы к Telegram и Groq идут через одну CF-ссылку.

Если CF_PROXY_URL не задан — работает напрямую (удобно для dev).
"""

import httpx
from ..config import settings


def build_telegram_client() -> httpx.AsyncClient:
    """
    CF Worker принимает запросы вида:
        {CF_PROXY_URL}/telegram/botTOKEN/METHOD
    и проксирует их на:
        https://api.telegram.org/botTOKEN/METHOD
    """
    if settings.CF_PROXY_URL:
        base_url = f"{settings.CF_PROXY_URL.rstrip('/')}/telegram"
    else:
        base_url = "https://api.telegram.org"

    return httpx.AsyncClient(
        base_url=base_url,
        timeout=httpx.Timeout(30.0),
    )


def build_groq_client() -> httpx.AsyncClient:
    """
    CF Worker принимает запросы вида:
        {CF_PROXY_URL}/groq/openai/v1/chat/completions
    и проксирует их на:
        https://api.groq.com/openai/v1/chat/completions
    """
    if settings.CF_PROXY_URL:
        base_url = f"{settings.CF_PROXY_URL.rstrip('/')}/groq"
    else:
        base_url = "https://api.groq.com"

    return httpx.AsyncClient(
        base_url=base_url,
        headers={
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type":  "application/json",
        },
        timeout=httpx.Timeout(30.0),
    )