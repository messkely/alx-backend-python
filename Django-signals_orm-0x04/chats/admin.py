from django.contrib import admin
from .models import Message

@admin.register(Message)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'content_preview', 'timestamp', 'read')
    list_filter = ('timestamp', 'read', 'edited')
    search_fields = ('sender__username', 'receiver__username', 'content')
    readonly_fields = ('timestamp',)
    raw_id_fields = ('sender', 'receiver', 'parent_message')
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = "Content Preview"
