from datetime import datetime, timedelta, timezone


def convert_iso_time_str_to_datetime(s: str) -> datetime:
    dt = datetime.fromisoformat(s)
    return dt.astimezone(timezone(timedelta(hours=8)))
