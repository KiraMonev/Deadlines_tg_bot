from __future__ import annotations

from datetime import datetime


def parse_date(date_str: str) -> str | None:
    current_year = datetime.now().year
    separators = ['.', ' ', '-']

    for sep in separators:
        parts = date_str.split(sep)
        if len(parts) == 2:
            parts.append(str(current_year))  # Добавляем текущий год, если не указан
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
                if 0 <= hours <= 24 and 0 <= minutes <= 59:
                    return f"{hours:02}:{minutes:02}"
            except ValueError:
                return None
    return None