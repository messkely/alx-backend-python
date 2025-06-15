from django.contrib import admin
from .models import Message, Notification, MessageHistory

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'content_preview', 'timestamp', 'edited', 'edited_by', 'read')
    list_filter = ('timestamp', 'edited', 'read')
    search_fields = ('sender__username', 'receiver__username', 'content')
    readonly_fields = ('timestamp', 'edited_at')
    raw_id_fields = ('sender', 'receiver', 'edited_by', 'parent_message')
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = "Content Preview"
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('sender', 'receiver')
        return self.readonly_fields

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_preview', 'timestamp', 'read')
    list_filter = ('timestamp', 'read')
    search_fields = ('user__username', 'content')
    readonly_fields = ('timestamp',)
    raw_id_fields = ('user', 'message')
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = "Content Preview"

@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ('message', 'old_content_preview', 'edited_at')
    list_filter = ('edited_at',)
    readonly_fields = ('edited_at',)
    raw_id_fields = ('message',)
    
    def old_content_preview(self, obj):
        return obj.old_content[:50] + "..." if len(obj.old_content) > 50 else obj.old_content
    old_content_preview.short_description = "Old Content Preview"

