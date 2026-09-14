from datetime import datetime


def format_iso_datetime(dt: datetime) -> str:
    """Format datetime as ISO 8601 with Z suffix and milliseconds.
    
    Example: 2024-01-15T10:30:00.123Z
    """
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%dT%H:%M:%S.') + f'{dt.microsecond // 1000:03d}Z'
