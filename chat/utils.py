import json

from django.db import connection


def notify(*, channel: str, event: str, event_id: int, data: str) -> None:
    payload = json.dumps({
        "event": event,
        "event_id": event_id,
        "data": data,
    })
    with connection.cursor() as cursor:
        cursor.execute(
            f"NOTIFY {channel}, '{payload}'",
        )
