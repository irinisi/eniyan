from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

router = Router()

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📋 Мои задачи"),
            KeyboardButton(text="➕ Новая задача"),
        ],
        [
            KeyboardButton(text="📁 Все задачи"),
            KeyboardButton(text="🔍 Поиск"),
        ],
    ],
    resize_keyboard=True,
)


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет! Я бот TeamOS.\n\n"
        "Используй кнопки внизу или команды:\n"
        "/iam @username — привязать себя\n"
        "/tasks — мои задачи\n"
        "/newtask — создать задачу\n"
        "/alltasks — все задачи команды\n"
        "/search — поиск по базе знаний",
        reply_markup=MAIN_KEYBOARD,
    )


@router.message(F.text == "📋 Мои задачи")
async def btn_my_tasks(message: Message):
    from handlers.tasks import list_my_tasks
    await list_my_tasks(message)


@router.message(F.text == "➕ Новая задача")
async def btn_new_task(message: Message, state):
    from handlers.tasks import start_new_task
    await start_new_task(message, state)


@router.message(F.text == "📁 Все задачи")
async def btn_all_tasks(message: Message):
    from handlers.tasks import list_all_tasks
    await list_all_tasks(message)


@router.message(F.text == "🔍 Поиск")
async def btn_search(message: Message):
    await message.answer("Введи запрос: /search <текст>")
