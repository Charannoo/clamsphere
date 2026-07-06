from django.db import models
from django.contrib.auth.models import User


class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Chat histories"
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.user or 'Anonymous'} - {self.timestamp.strftime('%d %b %H:%M')}"
