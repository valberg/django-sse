import json
from collections.abc import AsyncGenerator

import psycopg
from django.db import connection
from django.http import HttpRequest, HttpResponse
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from chat.models import ChatMessage
from chat.utils import notify


async def stream_messages() -> AsyncGenerator[str, None]:
    connection_params = connection.get_connection_params()

    # Remove the cursor_factory parameter since I can't get
    # the default from Django 4.2.1 to work.
    # Django 4.2 didn't have the parameter and that worked.
    connection_params.pop('cursor_factory')

    aconnection = await psycopg.AsyncConnection.connect(
        **connection_params,
        autocommit=True,
    )
    channel_name = "lobby"
    async with aconnection.cursor() as acursor:
        await acursor.execute(f"LISTEN {channel_name}")
        gen = aconnection.notifies()
        async for notify in gen:
            payload = json.loads(notify.payload)
            event = payload.pop("event")
            data = payload.pop("data")
            yield f"event: {event}\ndata: {data}\n\n"


async def stream_messages_view(
    request: HttpRequest,
) -> StreamingHttpResponse:
    return StreamingHttpResponse(
        streaming_content=stream_messages(),
        content_type="text/event-stream",
    )


@csrf_exempt
@require_POST
def post_message_view(request: HttpRequest) -> HttpResponse:
    message = request.POST.get("message")
    user = request.POST.get("user")
    message = ChatMessage.objects.create(user=user, text=message)
    notify(
        channel="lobby",
        event="message_created",
        data=json.dumps({
            "text": message.text,
            "user": message.user,
        })
    )
    return HttpResponse("OK")
