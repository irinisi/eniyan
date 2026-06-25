from datetime import date

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

import api_client
from date_parsing import DateParseError, parse_due

router = Router()

STATUS_LABELS = {
    "todo": "Todo",
    "in_progress": "In Progress",
    "review": "Review",
    "done": "Done",
}


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
    await message.answer(
        "Срок? Примеры: '-' (без срока), 'сегодня', 'завтра', '15' (число этого/следующего месяца), "
        "'12.08', 'через неделю', 'через 3 дня', 'пятницу'"
    )


@router.message(NewTask.due)
async def task_due(message: Message, state: FSMContext):
    try:
        due = parse_due(message.text, date.today())
    except DateParseError as exc:
        await message.answer(str(exc))
        return
    data = await state.get_data()
    payload = {
        "title": data["title"],
        "assignee": data["assignee"],
        "due": due.isoformat() if due else None,
    }
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
    for task in open_tasks:
        text = f"{task['title']} — {STATUS_LABELS[task['status']]} ({task.get('assignee') or 'без исполнителя'})"
        await message.answer(text, reply_markup=task_quick_actions_keyboard(task["id"]))


def task_quick_actions_keyboard(task_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✔ Выполнить", callback_data=f"task:done:{task_id}"),
                InlineKeyboardButton(text="🔄 Статус", callback_data=f"task:status:{task_id}"),
            ],
        ]
    )


def task_status_keyboard(task_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, callback_data=f"task:setstatus:{task_id}:{status}")]
            for status, label in STATUS_LABELS.items()
        ]
        + [[InlineKeyboardButton(text="← Назад", callback_data=f"task:back:{task_id}")]]
    )


@router.callback_query(F.data.startswith("task:done:"))
async def complete_task(callback: CallbackQuery):
    task_id = callback.data.split(":")[-1]
    await api_client.update_task(task_id, {"status": "done"})
    await callback.answer("Задача выполнена")
    await callback.message.edit_text(f"{callback.message.text}\n\n✔ Выполнено")


@router.callback_query(F.data.startswith("task:status:"))
async def choose_status(callback: CallbackQuery):
    task_id = callback.data.split(":")[-1]
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=task_status_keyboard(task_id))


@router.callback_query(F.data.startswith("task:back:"))
async def back_to_actions(callback: CallbackQuery):
    task_id = callback.data.split(":")[-1]
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=task_quick_actions_keyboard(task_id))


@router.callback_query(F.data.startswith("task:setstatus:"))
async def set_status(callback: CallbackQuery):
    _, _, task_id, status = callback.data.split(":")
    await api_client.update_task(task_id, {"status": status})
    await callback.answer(f"Статус: {STATUS_LABELS[status]}")
    await callback.message.edit_reply_markup(reply_markup=task_quick_actions_keyboard(task_id))
