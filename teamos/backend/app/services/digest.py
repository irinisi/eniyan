from __future__ import annotations

from datetime import date

from app.services.tasks import list_tasks


def build_daily_digest(today: date | None = None) -> str:
    today = today or date.today()
    tasks = list_tasks()

    due_today = [t for t in tasks if t.due == today and t.status != "done"]
    overdue = [t for t in tasks if t.due and t.due < today and t.status != "done"]

    lines = ["*Утренний дайджест*", ""]
    lines.append(f"Сегодня:\n— {len(due_today)} задач" if due_today else "Сегодня: нет задач")
    for t in due_today:
        lines.append(f"  • {t.title} ({t.assignee or 'без исполнителя'})")

    lines.append("")
    lines.append(f"Просрочено:\n— {len(overdue)} задач" if overdue else "Просрочено: нет")
    for t in overdue:
        lines.append(f"  • {t.title} (срок {t.due})")

    return "\n".join(lines)
