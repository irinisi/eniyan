"""Daily digest notification at 12:00 — sends each user their tasks due today or overdue."""
from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime, timedelta, timezone

from aiogram import Bot

import api_client
import user_registry

log = logging.getLogger(__name__)

# UTC offset for Moscow time (UTC+3)
TZ_OFFSET = 3


def _seconds_until_noon() -> float:
    now_utc = datetime.now(timezone.utc)
    now_local = now_utc + timedelta(hours=TZ_OFFSET)
    target = now_local.replace(hour=12, minute=0, second=0, microsecond=0)
    if now_local >= target:
        target += timedelta(days=1)
    return (target - now_local).total_seconds()


async def _send_daily_digest(bot: Bot) -> None:
    registrations = user_registry.all_registrations()
    if not registrations:
        return
    try:
        tasks = await api_client.get_tasks()
    except Exception as exc:
        log.warning("notifier: failed to fetch tasks: %s", exc)
        return

    today = date.today()
    open_tasks = [t for t in tasks if t["status"] != "done"]

    for telegram_id_str, assignee in registrations.items():
        my_tasks = [t for t in open_tasks if t.get("assignee") == assignee]
        if not my_tasks:
            continue

        due_today = [t for t in my_tasks if t.get("due") == str(today)]
        overdue = [t for t in my_tasks if t.get("due") and t["due"] < str(today)]

        lines = [f"☀️ <b>Доброго дня, {assignee}!</b>\n"]
        if due_today:
            lines.append("📅 <b>На сегодня:</b>")
            for t in due_today:
                lines.append(f"  • {t['title']}")
        if overdue:
            lines.append("\n⚠️ <b>Просрочено:</b>")
            for t in overdue:
                lines.append(f"  • {t['title']} (срок: {t['due']})")
        if not due_today and not overdue:
            continue

        try:
            await bot.send_message(int(telegram_id_str), "\n".join(lines), parse_mode="HTML")
        except Exception as exc:
            log.warning("notifier: failed to send to %s: %s", telegram_id_str, exc)


async def daily_notifier_loop(bot: Bot) -> None:
    while True:
        delay = _seconds_until_noon()
        log.info("notifier: next digest in %.0f seconds", delay)
        await asyncio.sleep(delay)
        await _send_daily_digest(bot)
        await asyncio.sleep(60)  # avoid double-fire within same minute
