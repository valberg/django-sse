import json
from collections.abc import AsyncGenerator

import psycopg
from django.db import connection
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from chat.models import ChatMessage
from chat.utils import notify
from chat.utils import sse_message


async def stream_messages(last_id: int | None = None) -> AsyncGenerator[str, None]:
    connection_params = connection.get_connection_params()

    # Remove the cursor_factory parameter since I can't get
    # the default from Django 4.2.1 to work.
    # Django 4.2 didn't have the parameter and that worked.
    connection_params.pop("cursor_factory")

    aconnection = await psycopg.AsyncConnection.connect(
        **connection_params,
        autocommit=True,
    )
    channel_name = "lobby"

    # Uncomment the following to generate random message to
    # test that we are streaming messages that are created
    # while the client is disconnected.

    # await ChatMessage.objects.acreate(
    #     user="system",
    #     text="randomly generated", room=channel_name)

    if last_id:
        messages = ChatMessage.objects.filter(id__gt=last_id)
        async for message in messages:
            yield sse_message(
                event="message_created",
                event_id=message.id,
                data=message.as_json(),
            )

    async with aconnection.cursor() as acursor:
        await acursor.execute(f"LISTEN {channel_name}")
        gen = aconnection.notifies()
        async for notify_message in gen:
            payload = json.loads(notify_message.payload)
            event = payload.get("event")
            event_id = payload.get("event_id")
            data = payload.get("data")
            yield sse_message(
                event=event,
                event_id=event_id,
                data=data,
            )


async def stream_messages_view(
    request: HttpRequest,
) -> StreamingHttpResponse:
    last_id = request.headers.get("Last-Event-ID")
    return StreamingHttpResponse(
        streaming_content=stream_messages(last_id=last_id),
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
        event_id=message.id,
        data=message.as_json(),
    )
    return HttpResponse("OK")
