from datetime import datetime, timezone


def iso_to_timestamp(iso_str: str) -> float:
    """
    Converts ISO 8601 string with 'Z' suffix to Unix timestamp.

    Args:
        iso_str (str): ISO datetime string, e.g., '2025-03-19T18:11:35.321933Z'

    Returns:
        float: Unix timestamp
    """
    dt = datetime.strptime(iso_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()