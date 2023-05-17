"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import path

from chat.models import ChatMessage
from chat.views import stream_messages_view, post_message_view


def lobby(request: HttpRequest) -> HttpResponse:

    return render(
        request,
        "lobby.html",
        context={"messages": ChatMessage.objects.all().order_by("-id")}
    )


urlpatterns = [
    path("", lobby, name="lobby"),
    path("messages/", stream_messages_view, name="stream-messages"),
    path("new_message/", post_message_view, name="new-message"),
    path('admin/', admin.site.urls),
]
