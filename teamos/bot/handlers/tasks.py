from datetime import date

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

import api_client
import user_registry
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
    project = State()
    due = State()


def project_choice_keyboard(projects: list[dict]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=p["title"], callback_data=f"newtask:project:{p['id']}")]
            for p in projects
        ]
        + [[InlineKeyboardButton(text="Без проекта", callback_data="newtask:project:")]]
    )


def assignee_choice_keyboard(assignees: list[str]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=a, callback_data=f"newtask:assignee:{a}")]
            for a in assignees
        ]
        + [[InlineKeyboardButton(text="✍ Ввести вручную", callback_data="newtask:assignee:")]]
    )


def telegram_link(assignee: str | None) -> str:
    if not assignee:
        return "без исполнителя"
    username = assignee.strip().lstrip("@")
    if username.replace("_", "").isalnum():
        return f'<a href="https://t.me/{username}">{assignee}</a>'
    return assignee


async def ask_project(message: Message, state: FSMContext):
    await state.set_state(NewTask.project)
    projects = await api_client.get_projects()
    if not projects:
        await state.update_data(project=None)
        await state.set_state(NewTask.due)
        await message.answer(
            "Срок? Примеры: '-' (без срока), 'сегодня', 'завтра', '15' (число этого/следующего месяца), "
            "'12.08', 'через неделю', 'через 3 дня', 'пятницу'"
        )
        return
    await message.answer("Выбери проект:", reply_markup=project_choice_keyboard(projects))


@router.message(Command("newtask"))
async def start_new_task(message: Message, state: FSMContext):
    await state.set_state(NewTask.title)
    await message.answer("Название задачи?")


@router.message(NewTask.title)
async def task_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(NewTask.assignee)
    tasks = await api_client.get_tasks()
    assignees = sorted({t["assignee"] for t in tasks if t.get("assignee")})
    if not assignees:
        await message.answer("Кто исполнитель? (имя или telegram id)")
        return
    await message.answer("Кто исполнитель?", reply_markup=assignee_choice_keyboard(assignees))


@router.message(NewTask.assignee)
async def task_assignee(message: Message, state: FSMContext):
    await state.update_data(assignee=message.text)
    await ask_project(message, state)


@router.callback_query(NewTask.assignee, F.data.startswith("newtask:assignee:"))
async def task_assignee_choice(callback: CallbackQuery, state: FSMContext):
    assignee = callback.data.split(":", 2)[2]
    await callback.answer()
    if not assignee:
        await callback.message.answer("Кто исполнитель? (имя или telegram id)")
        return
    await state.update_data(assignee=assignee)
    await ask_project(callback.message, state)


@router.callback_query(NewTask.project, F.data.startswith("newtask:project:"))
async def task_project(callback: CallbackQuery, state: FSMContext):
    project_id = callback.data.split(":", 2)[2] or None
    await state.update_data(project=project_id)
    await state.set_state(NewTask.due)
    await callback.answer()
    await callback.message.answer(
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
        "project": data.get("project"),
        "due": due.isoformat() if due else None,
    }
    task = await api_client.create_task(payload)
    await state.clear()
    await message.answer(f"Задача создана: {task['title']} ({task['id']})")


@router.message(Command("iam"))
async def set_identity(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        assignee = message.from_user.username
        if not assignee:
            await message.answer("Укажи своё имя: /iam @username или /iam Имя")
            return
        assignee = f"@{assignee}"
    else:
        assignee = parts[1].strip()
    user_registry.register(message.from_user.id, assignee)
    await message.answer(f"Готово! Теперь /tasks будет показывать задачи для <b>{assignee}</b>.", parse_mode="HTML")


@router.message(Command("tasks"))
async def list_my_tasks(message: Message):
    assignee = user_registry.get_assignee(message.from_user.id)
    tasks = await api_client.get_tasks()
    if assignee:
        open_tasks = [t for t in tasks if t["status"] != "done" and t.get("assignee") == assignee]
    else:
        open_tasks = [t for t in tasks if t["status"] != "done"]
    if not open_tasks:
        hint = f" для {assignee}" if assignee else ""
        reg_hint = "" if assignee else "\n\nСовет: используй /iam @username чтобы видеть только свои задачи."
        await message.answer(f"Нет активных задач{hint} 🎉{reg_hint}")
        return
    for task in open_tasks:
        text = f"{task['title']} — {STATUS_LABELS[task['status']]} ({telegram_link(task.get('assignee'))})"
        await message.answer(text, reply_markup=task_quick_actions_keyboard(task["id"]), parse_mode="HTML")


@router.message(Command("alltasks"))
async def list_all_tasks(message: Message):
    tasks = await api_client.get_tasks()
    open_tasks = [t for t in tasks if t["status"] != "done"]
    if not open_tasks:
        await message.answer("Нет активных задач 🎉")
        return
    for task in open_tasks:
        text = f"{task['title']} — {STATUS_LABELS[task['status']]} ({telegram_link(task.get('assignee'))})"
        await message.answer(text, reply_markup=task_quick_actions_keyboard(task["id"]), parse_mode="HTML")


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
