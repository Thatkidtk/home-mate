from __future__ import annotations

from datetime import date, datetime


def parse_iso_date(value: str | None) -> date | None:
    """Parse YYYY-MM-DD to date, returning None on blank/invalid."""
    value = (value or "").strip()
    if not value:
        return None
    try:
        # fromisoformat handles YYYY-MM-DD
        return date.fromisoformat(value)
    except ValueError:
        try:
            # Sometimes browsers send full datetime strings.
            return datetime.fromisoformat(value).date()
        except ValueError:
            return None
