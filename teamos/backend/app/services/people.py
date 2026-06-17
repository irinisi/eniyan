from __future__ import annotations

from app.config import PEOPLE_DIR
from app.models.schemas import Person
from app.services.markdown_store import list_entities, read_entity


def _to_person(entity: dict) -> Person:
    fm = entity["frontmatter"]
    return Person(
        id=fm.get("id", entity["path"].stem),
        name=fm.get("name", entity["path"].stem),
        role=fm.get("role", "member"),
        telegram_id=fm.get("telegram_id"),
    )


def list_people() -> list[Person]:
    return [_to_person(e) for e in list_entities(PEOPLE_DIR)]


def get_person(person_id: str) -> Person | None:
    path = PEOPLE_DIR / f"{person_id}.md"
    if not path.exists():
        return None
    return _to_person(read_entity(path))


def get_person_by_telegram_id(telegram_id: int) -> Person | None:
    for person in list_people():
        if person.telegram_id == telegram_id:
            return person
    return None
