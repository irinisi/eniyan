from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, WebAppInfo

from config import MINIAPP_URL

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🏠 Открыть TeamOS", web_app=WebAppInfo(url=MINIAPP_URL))]],
        resize_keyboard=True,
    )
    await message.answer(
        "Привет! Я бот TeamOS.\n\n"
        "Команды:\n"
        "/tasks — мои задачи\n"
        "/newtask — создать задачу\n"
        "/deltask <id> — удалить задачу\n"
        "/search <запрос> — поиск по базе знаний\n",
        reply_markup=keyboard,
    )
