from django.db import models
from django.contrib.auth.models import User

class MoodEntry(models.Model):

    MOOD_CHOICES = [
        ('happy', '😊 Happy'),
        ('sad', '😢 Sad'),
        ('stress', '😫 Stress'),
        ('calm', '😌 Calm'),
        ('angry', '😡 Angry'),
        ('excited', '🤩 Excited'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.mood}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    mobile = models.CharField(max_length=20, unique=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} profile"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    notif_type = models.CharField(max_length=50, default='general')

    def __str__(self):
        return f"{self.user.username} - {self.notif_type} - {'Read' if self.is_read else 'Unread'}"

