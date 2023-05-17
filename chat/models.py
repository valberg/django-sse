from django.db import models


class ChatMessage(models.Model):
    user = models.CharField(max_length=255)
    text = models.CharField(max_length=255)