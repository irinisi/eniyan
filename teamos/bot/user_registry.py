"""Persist telegram_id → assignee mapping in a JSON file."""
from __future__ import annotations

import json
import os
from pathlib import Path

_REGISTRY_PATH = Path(os.environ.get("TEAMOS_REGISTRY_PATH", "/data/user_registry.json"))


def _load() -> dict[str, str]:
    if not _REGISTRY_PATH.exists():
        return {}
    try:
        return json.loads(_REGISTRY_PATH.read_text())
    except Exception:
        return {}


def _save(data: dict[str, str]) -> None:
    _REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    _REGISTRY_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def register(telegram_id: int, assignee: str) -> None:
    data = _load()
    data[str(telegram_id)] = assignee
    _save(data)


def get_assignee(telegram_id: int) -> str | None:
    return _load().get(str(telegram_id))


def all_registrations() -> dict[str, str]:
    """Return {telegram_id_str: assignee} for all registered users."""
    return _load()
