from datetime import datetime, date, timedelta
from typing import Optional


def utcnow() -> datetime:
    return datetime.utcnow()


def today() -> date:
    return date.today()


def parse_date(value: Optional[str]) -> Optional[date]:
    if not value or not str(value).strip():
        return None
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def add_days(base: Optional[date] = None, days: int = 3) -> date:
    start = base or today()
    return start + timedelta(days=days)


def is_overdue(due: date, status: str) -> bool:
    if status in ("Completed", "Cancelled"):
        return False
    return due < today()
