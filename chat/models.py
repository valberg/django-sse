import json

from django.db import models


class ChatMessage(models.Model):
    user = models.CharField(max_length=255)
    text = models.CharField(max_length=255)
    room = models.CharField(max_length=255, default="lobby")

    def as_json(self):
        return json.dumps(
            {
                "id": self.id,
                "user": self.user,
                "text": self.text,
                "room": self.room,
            },
        )
