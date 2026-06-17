import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from handlers import common, knowledge, tasks


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(common.router)
    dp.include_router(tasks.router)
    dp.include_router(knowledge.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
