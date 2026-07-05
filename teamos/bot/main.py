import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import BOT_TOKEN
from handlers import common, knowledge, tasks
from notifier import daily_notifier_loop

COMMANDS = [
    BotCommand(command="tasks", description="Мои активные задачи"),
    BotCommand(command="newtask", description="Создать новую задачу"),
    BotCommand(command="alltasks", description="Все активные задачи команды"),
    BotCommand(command="iam", description="Привязать себя: /iam @username"),
    BotCommand(command="search", description="Поиск по базе знаний"),
    BotCommand(command="start", description="Главное меню"),
]


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN)
    await bot.set_my_commands(COMMANDS)
    dp = Dispatcher()
    dp.include_router(common.router)
    dp.include_router(tasks.router)
    dp.include_router(knowledge.router)
    asyncio.create_task(daily_notifier_loop(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
