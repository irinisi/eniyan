import re
from datetime import date, timedelta

_RELATIVE_DAYS = {
    "сегодня": 0,
    "завтра": 1,
    "послезавтра": 2,
}

_UNIT_DAYS = {
    "день": 1, "дня": 1, "дней": 1,
    "неделю": 7, "недели": 7, "недель": 7,
    "месяц": 30, "месяца": 30, "месяцев": 30,
}


def parse_due(text: str, today: date | None = None) -> date | None:
    """Parse a Russian-language due date. Returns None for "no deadline",
    raises ValueError if the text can't be understood."""
    today = today or date.today()
    text = text.strip().lower()

    if text == "-":
        return None

    if text in _RELATIVE_DAYS:
        return today + timedelta(days=_RELATIVE_DAYS[text])

    match = re.fullmatch(r"через\s+(\d+)?\s*([а-я]+)", text)
    if match:
        count = int(match.group(1)) if match.group(1) else 1
        unit_days = _UNIT_DAYS.get(match.group(2))
        if unit_days is not None:
            return today + timedelta(days=count * unit_days)

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return date.fromisoformat(text)

    if re.fullmatch(r"\d{1,2}", text):
        day = int(text)
        candidate = today.replace(day=day) if day <= 28 or day <= _days_in_month(today) else None
        if candidate is None:
            raise ValueError(f"Некорректный день месяца: {day}")
        if candidate < today:
            candidate = _add_month(candidate)
        return candidate

    match = re.fullmatch(r"(\d{1,2})\.(\d{1,2})(?:\.(\d{4}))?", text)
    if match:
        day, month = int(match.group(1)), int(match.group(2))
        year = int(match.group(3)) if match.group(3) else today.year
        candidate = date(year, month, day)
        if not match.group(3) and candidate < today:
            candidate = date(year + 1, month, day)
        return candidate

    raise ValueError(f"Не понимаю дату: {text!r}")


def _days_in_month(d: date) -> int:
    next_month = _add_month(d.replace(day=1))
    return (next_month - timedelta(days=1)).day


def _add_month(d: date) -> date:
    if d.month == 12:
        return d.replace(year=d.year + 1, month=1)
    return d.replace(month=d.month + 1)
