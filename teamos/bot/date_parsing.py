import re
from datetime import date, timedelta

WEEKDAYS = {
    "понедельник": 0,
    "вторник": 1,
    "среда": 2,
    "среду": 2,
    "четверг": 3,
    "пятница": 4,
    "пятницу": 4,
    "суббота": 5,
    "субботу": 5,
    "воскресенье": 6,
}


class DateParseError(ValueError):
    pass


def _add_months(d: date, months: int) -> date:
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    day = min(d.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return date(year, month, day)


def parse_due(text: str, today: date) -> date | None:
    raw = text.strip().lower()
    if raw in ("-", ""):
        return None
    if raw == "сегодня":
        return today
    if raw == "завтра":
        return today + timedelta(days=1)
    if raw == "послезавтра":
        return today + timedelta(days=2)

    m = re.fullmatch(r"через (\d+) (день|дня|дней)", raw)
    if m:
        return today + timedelta(days=int(m.group(1)))

    m = re.fullmatch(r"через (\d+) (недел[юяи])", raw)
    if m:
        return today + timedelta(weeks=int(m.group(1)))

    if raw == "через неделю":
        return today + timedelta(weeks=1)

    m = re.fullmatch(r"через (\d+) месяц(?:а|ев)?", raw)
    if m:
        return _add_months(today, int(m.group(1)))

    if raw == "через месяц":
        return _add_months(today, 1)

    if raw in WEEKDAYS:
        target = WEEKDAYS[raw]
        delta = (target - today.weekday()) % 7
        return today + timedelta(days=delta or 7)

    # full ISO date: YYYY-MM-DD
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", raw)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError as exc:
            raise DateParseError("Некорректная дата") from exc

    # DD.MM or DD.MM.YYYY
    m = re.fullmatch(r"(\d{1,2})\.(\d{1,2})(?:\.(\d{4}))?", raw)
    if m:
        day, month = int(m.group(1)), int(m.group(2))
        year = int(m.group(3)) if m.group(3) else today.year
        try:
            return date(year, month, day)
        except ValueError as exc:
            raise DateParseError("Некорректная дата") from exc

    # just a day number -> nearest occurrence in current (or next) year
    m = re.fullmatch(r"(\d{1,2})", raw)
    if m:
        day = int(m.group(1))
        try:
            candidate = date(today.year, today.month, day)
        except ValueError as exc:
            raise DateParseError("Некорректное число месяца") from exc
        if candidate < today:
            next_month = _add_months(date(today.year, today.month, 1), 1)
            try:
                candidate = date(next_month.year, next_month.month, day)
            except ValueError as exc:
                raise DateParseError("Некорректное число месяца") from exc
        return candidate

    raise DateParseError(
        "Не понял дату. Примеры: '-', 'сегодня', 'завтра', '15' (число этого/следующего месяца), "
        "'12.08', 'через неделю', 'через 3 дня', 'пятницу'"
    )
