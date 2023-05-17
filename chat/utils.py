import json

from django.db import connection


def notify(*, channel: str, event: str, data: str) -> None:
    payload = json.dumps({
        "event": event,
        "data": data,
    })
    with connection.cursor() as cursor:
        cursor.execute(
            f"NOTIFY {channel}, '{payload}'",
        )
