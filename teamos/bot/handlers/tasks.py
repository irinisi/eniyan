from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

import api_client

router = Router()


class NewTask(StatesGroup):
    title = State()
    assignee = State()
    due = State()


@router.message(Command("newtask"))
async def start_new_task(message: Message, state: FSMContext):
    await state.set_state(NewTask.title)
    await message.answer("Название задачи?")


@router.message(NewTask.title)
async def task_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(NewTask.assignee)
    await message.answer("Кто исполнитель? (имя или telegram id)")


@router.message(NewTask.assignee)
async def task_assignee(message: Message, state: FSMContext):
    await state.update_data(assignee=message.text)
    await state.set_state(NewTask.due)
    await message.answer("Срок? (YYYY-MM-DD, или '-' если без срока)")


@router.message(NewTask.due)
async def task_due(message: Message, state: FSMContext):
    data = await state.get_data()
    due = None if message.text.strip() == "-" else message.text.strip()
    payload = {"title": data["title"], "assignee": data["assignee"], "due": due}
    task = await api_client.create_task(payload)
    await state.clear()
    await message.answer(f"Задача создана: {task['title']} ({task['id']})")


@router.message(Command("tasks"))
async def list_my_tasks(message: Message):
    tasks = await api_client.get_tasks()
    open_tasks = [t for t in tasks if t["status"] != "done"]
    if not open_tasks:
        await message.answer("Нет активных задач 🎉")
        return
    lines = [f"• {t['title']} — {t['status']} ({t.get('assignee') or 'без исполнителя'})" for t in open_tasks]
    await message.answer("\n".join(lines))


def task_quick_actions_keyboard(task_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✔ Выполнить", callback_data=f"task:done:{task_id}"),
                InlineKeyboardButton(text="📅 Перенести", callback_data=f"task:postpone:{task_id}"),
            ],
            [
                InlineKeyboardButton(text="👤 Назначить", callback_data=f"task:assign:{task_id}"),
                InlineKeyboardButton(text="✏ Открыть", callback_data=f"task:open:{task_id}"),
            ],
        ]
    )


@router.callback_query(F.data.startswith("task:done:"))
async def complete_task(callback: CallbackQuery):
    task_id = callback.data.split(":")[-1]
    await api_client.update_task(task_id, {"status": "done"})
    await callback.answer("Задача выполнена")
    await callback.message.edit_text(f"{callback.message.text}\n\n✔ Выполнено")
