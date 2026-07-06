from django.contrib import admin
from .models import MoodEntry, UserProfile, Notification

@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'mood', 'created_at']
    list_filter = ['mood', 'created_at']
    search_fields = ['user__username']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'mobile', 'is_admin']
    search_fields = ['user__username', 'mobile']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notif_type', 'is_read', 'created_at']
    list_filter = ['is_read', 'notif_type', 'created_at']
    search_fields = ['user__username', 'message']

