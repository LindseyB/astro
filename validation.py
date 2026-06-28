"""Shared request and birth-data validation helpers."""

import re
from datetime import date, datetime, timedelta
from typing import Any
from collections.abc import Mapping, Sequence


def _decimal_to_astro_coord(value: Any, is_latitude: bool) -> Any:
    """Convert decimal coordinates to flatlib astro format (e.g., 40n42, 74w00)."""
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return value

    direction = 'n' if is_latitude else 'e'
    if numeric < 0:
        direction = 's' if is_latitude else 'w'

    absolute = abs(numeric)
    degrees = int(absolute)
    minutes = int(round((absolute - degrees) * 60))
    if minutes == 60:
        degrees += 1
        minutes = 0

    return f"{degrees}{direction}{minutes:02d}"


def _normalize_birth_inputs(
    birth_date: str | None,
    timezone_offset: str | None,
    latitude: str | None,
    longitude: str | None,
) -> tuple[str | None, str | None, str | None, str | None]:
    """Normalize legacy input formats used by older saved form data."""
    if isinstance(birth_date, str):
        birth_date = birth_date.strip()
        if '/' in birth_date:
            birth_date = birth_date.replace('/', '-')

    if isinstance(timezone_offset, str):
        timezone_offset = timezone_offset.strip()
        tz_match = re.fullmatch(r'([+-]?)(\d{1,2})', timezone_offset)
        if tz_match:
            sign, hours = tz_match.groups()
            hour_num = int(hours)
            if sign == '':
                sign = '-' if timezone_offset.startswith('-') else '+'
            timezone_offset = f"{sign}{hour_num:02d}:00"

    if isinstance(latitude, str):
        latitude = latitude.strip().lower()
    if isinstance(longitude, str):
        longitude = longitude.strip().lower()

    lat_pattern = r'^\d+[ns]\d{1,2}$'
    lon_pattern = r'^\d+[we]\d{1,2}$'

    if isinstance(latitude, str) and latitude and not re.fullmatch(lat_pattern, latitude):
        latitude = _decimal_to_astro_coord(latitude, is_latitude=True)
    if isinstance(longitude, str) and longitude and not re.fullmatch(lon_pattern, longitude):
        longitude = _decimal_to_astro_coord(longitude, is_latitude=False)

    return birth_date, timezone_offset, latitude, longitude


def _parse_timezone_offset_minutes(timezone_offset: object) -> int:
    """Parse timezone offsets like -5, +05:00, or +0530 into minutes."""
    if not isinstance(timezone_offset, str):
        return 0

    tz = timezone_offset.strip()
    match = re.fullmatch(r'([+-]?)(\d{1,2})(?::?(\d{2}))?', tz)
    if not match:
        return 0

    sign_token, hours_text, minutes_text = match.groups()
    sign = -1 if sign_token == '-' else 1
    hours = int(hours_text)
    minutes = int(minutes_text or '0')
    return sign * (hours * 60 + minutes)


def _get_user_local_today(timezone_offset: object) -> date:
    """Return today's date using the provided timezone offset."""
    offset_minutes = _parse_timezone_offset_minutes(timezone_offset)
    return (datetime.utcnow() + timedelta(minutes=offset_minutes)).date()


def _is_birthday_today(birth_date_html: object, timezone_offset: object) -> bool:
    """True if the user's birthday (month/day) matches their local date."""
    try:
        birthday = datetime.strptime(birth_date_html, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return False

    local_today = _get_user_local_today(timezone_offset)
    return (birthday.month, birthday.day) == (local_today.month, local_today.day)


def _format_birth_date_for_calculations(birth_date_text: object) -> str:
    """Validate supported birth date formats and return YYYY/MM/DD."""
    if not isinstance(birth_date_text, str):
        raise ValueError('Birth date must be a string in YYYY-MM-DD or YYYY/MM/DD format')

    normalized = birth_date_text.strip()
    for date_format in ('%Y-%m-%d', '%Y/%m/%d'):
        try:
            parsed = datetime.strptime(normalized, date_format)
            return parsed.strftime('%Y/%m/%d')
        except ValueError:
            continue

    raise ValueError('Birth date must be in YYYY-MM-DD or YYYY/MM/DD format')


def find_missing_fields(data: Mapping[str, object] | None, required_fields: Sequence[str]) -> list[str]:
    """Return missing required field names, allowing numeric zero values."""
    data = data or {}
    return [
        field for field in required_fields
        if field not in data or data.get(field) is None or data.get(field) == ''
    ]
