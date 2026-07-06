from django.contrib import admin
from .models import Journal

@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    list_display = ['username', 'date', 'content']
    list_filter = ['date']
    search_fields = ['username', 'content']
