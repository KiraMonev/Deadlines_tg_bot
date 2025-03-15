from __future__ import annotations

from datetime import datetime


def parse_date(date_str: str) -> str | None:
    current_year = datetime.now().year
    separators = ['.', ' ', '-']

    for sep in separators:
        parts = date_str.split(sep)
        if len(parts) == 2:
            parts.append(str(current_year))  # Текущий год, если не указан
        if len(parts) == 3:
            try:
                return datetime.strptime(".".join(parts), "%d.%m.%Y").strftime("%d.%m.%Y")
            except ValueError:
                return None
    return None


def parse_time(time_str: str) -> str | None:
    separators = ['.', ' ', '-', ':']

    for sep in separators:
        parts = time_str.split(sep)
        if len(parts) == 2:
            try:
                hours, minutes = int(parts[0]), int(parts[1])
                if 0 <= hours <= 23 and 0 <= minutes <= 59:
                    return f"{hours:02}:{minutes:02}"
            except ValueError:
                return None
    return None


async def calculate_reminder(reminder_offset, date, time) -> tuple:
    if not reminder_offset:
        return None, None

    deadline_date = datetime.strptime(date, "%d.%m.%Y")
    deadline_time = datetime.strptime(time, "%H:%M").time()

    deadline_datetime = datetime.combine(deadline_date, deadline_time)

    reminder_datetime = deadline_datetime - reminder_offset

    reminder_date = reminder_datetime.strftime("%d.%m.%Y")
    reminder_time = reminder_datetime.strftime("%H:%M")

    return reminder_date, reminder_time
