from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

import api_client

router = Router()


@router.message(Command("search"))
async def search(message: Message, command: CommandObject):
    query = command.args
    if not query:
        await message.answer("Использование: /search <запрос>")
        return
    docs = await api_client.search_knowledge(query)
    if not docs:
        await message.answer("Ничего не найдено")
        return
    lines = [f"• {d['title']} ({d['id']})" for d in docs[:10]]
    await message.answer("\n".join(lines))
