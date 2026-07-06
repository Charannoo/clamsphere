from django.contrib import admin
from .models import ChatHistory

@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'message', 'timestamp']
    list_filter = ['timestamp']
