from __future__ import annotations

from app.config import TASKS_DIR
from app.models.schemas import Task, TaskCreate, TaskUpdate
from app.services.markdown_store import delete_entity, list_entities, read_entity, slugify, write_entity


def _next_id() -> str:
    existing = [p.stem for p in TASKS_DIR.glob("task-*.md")] if TASKS_DIR.exists() else []
    numbers = []
    for name in existing:
        suffix = name.removeprefix("task-")
        if suffix.isdigit():
            numbers.append(int(suffix))
    return f"task-{(max(numbers) + 1) if numbers else 1:03d}"


def _to_task(entity: dict) -> Task:
    fm = entity["frontmatter"]
    return Task(
        id=fm.get("id", entity["path"].stem),
        title=fm.get("title", ""),
        description=entity["body"].strip(),
        status=fm.get("status", "todo"),
        assignee=fm.get("assignee"),
        project=fm.get("project"),
        priority=fm.get("priority", "medium"),
        due=fm.get("due"),
        tags=fm.get("tags", []) or [],
    )


def _path_for(task_id: str):
    return TASKS_DIR / f"{task_id}.md"


def list_tasks() -> list[Task]:
    return [_to_task(e) for e in list_entities(TASKS_DIR)]


def get_task(task_id: str) -> Task | None:
    path = _path_for(task_id)
    if not path.exists():
        return None
    return _to_task(read_entity(path))


def create_task(data: TaskCreate) -> Task:
    task_id = _next_id()
    frontmatter = {
        "id": task_id,
        "title": data.title,
        "status": "todo",
        "assignee": data.assignee,
        "project": data.project,
        "priority": data.priority.value,
        "due": data.due.isoformat() if data.due else None,
        "tags": data.tags,
    }
    write_entity(_path_for(task_id), frontmatter, data.description)
    return get_task(task_id)


def update_task(task_id: str, data: TaskUpdate) -> Task | None:
    path = _path_for(task_id)
    if not path.exists():
        return None
    entity = read_entity(path)
    fm = entity["frontmatter"]
    body = entity["body"]

    updates = data.model_dump(exclude_unset=True)
    if "description" in updates:
        body = updates.pop("description")
    for key, value in updates.items():
        if hasattr(value, "value"):
            value = value.value
        if hasattr(value, "isoformat"):
            value = value.isoformat()
        fm[key] = value

    write_entity(path, fm, body)
    return get_task(task_id)


def delete_task(task_id: str) -> bool:
    return delete_entity(_path_for(task_id))


def tasks_for_project(project_id: str) -> list[Task]:
    return [t for t in list_tasks() if t.project == project_id]
