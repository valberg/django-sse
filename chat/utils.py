import json

from django.db import connection


def notify(*, channel: str, event: str, event_id: int, data: str) -> None:
    payload = json.dumps(
        {
            "event": event,
            "event_id": event_id,
            "data": data,
        },
    )
    with connection.cursor() as cursor:
        cursor.execute(
            f"NOTIFY {channel}, '{payload}'",
        )


def sse_message(*, event: str, event_id: int, data: str) -> str:
    return f"id: {event_id}\n" f"event: {event}\n" f"data: {data}\n\n"
