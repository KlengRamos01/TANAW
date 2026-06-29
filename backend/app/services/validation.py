import re
from datetime import datetime

_MAX_SEARCH_LENGTH = 100
_MAX_NAME_LENGTH = 200
_MAX_REGION_LENGTH = 100

_SAFE_STRING_RE = re.compile(r"^[\w\s.\-,']+$")
_HTML_TAG_RE = re.compile(r"<[^>]*>")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def sanitize_string(value: str | None, max_length: int = _MAX_NAME_LENGTH) -> str:
    if not value:
        return ""
    cleaned = _HTML_TAG_RE.sub("", value.strip())
    cleaned = cleaned.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return cleaned[:max_length]


def validate_search_query(query: str) -> str:
    if not query or not query.strip():
        raise ValueError("Search query is required")
    cleaned = sanitize_string(query, _MAX_SEARCH_LENGTH)
    if len(cleaned) < 1:
        raise ValueError("Search query is empty after sanitization")
    return cleaned


def validate_destination_name(name: str | None) -> str | None:
    if not name:
        return None
    cleaned = sanitize_string(name)
    if not cleaned:
        return None
    return cleaned


def validate_date(date_str: str | None) -> str | None:
    if not date_str:
        return None
    cleaned = date_str.strip()
    if not _DATE_RE.match(cleaned):
        raise ValueError(f"Invalid date format: '{date_str}'. Expected YYYY-MM-DD.")
    try:
        datetime.strptime(cleaned, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date: '{cleaned}' is not a real calendar date.")
    if cleaned < "2020-01-01" or cleaned > "2100-12-31":
        raise ValueError(f"Date '{cleaned}' is out of valid range (2020-2100).")
    return cleaned


def validate_latitude(lat: float | None) -> float | None:
    if lat is None:
        return None
    if not isinstance(lat, (int, float)):
        raise ValueError("Latitude must be a number.")
    if lat < -90 or lat > 90:
        raise ValueError(f"Latitude {lat} is out of range (-90 to 90).")
    return float(lat)


def validate_longitude(lon: float | None) -> float | None:
    if lon is None:
        return None
    if not isinstance(lon, (int, float)):
        raise ValueError("Longitude must be a number.")
    if lon < -180 or lon > 180:
        raise ValueError(f"Longitude {lon} is out of range (-180 to 180).")
    return float(lon)


def validate_destination_id(dest_id: int | None) -> int | None:
    if dest_id is None:
        return None
    if not isinstance(dest_id, int) or dest_id <= 0:
        raise ValueError("Destination ID must be a positive integer.")
    return dest_id
