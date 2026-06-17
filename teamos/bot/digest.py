"""Daily 09:00 digest job. Run as a separate scheduled process (cron / APScheduler)."""
import asyncio

import httpx
from aiogram import Bot

from config import API_BASE_URL, BOT_TOKEN, DIGEST_CHAT_ID


async def send_daily_digest() -> None:
    if not DIGEST_CHAT_ID:
        raise RuntimeError("TEAMOS_DIGEST_CHAT_ID is not set")
    async with httpx.AsyncClient(base_url=API_BASE_URL) as client:
        resp = await client.get("/api/digest")
        resp.raise_for_status()
        text = resp.json()["text"]

    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(chat_id=DIGEST_CHAT_ID, text=text, parse_mode="Markdown")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(send_daily_digest())
