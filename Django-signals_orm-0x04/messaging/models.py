from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Add this class near the top of your file

class UnreadMessagesManager(models.Manager):
    def unread_for_user(self, user):
        return (
            self.get_queryset()
            .filter(receiver=user, read=False)
            .only('id', 'sender', 'receiver', 'content', 'timestamp')
        )


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    edited = models.BooleanField(default=False)
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='edited_messages')
    edited_at = models.DateTimeField(null=True, blank=True)
    read = models.BooleanField(default=False)
    parent_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['sender', 'receiver']),
            models.Index(fields=['receiver', 'read']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifications')
    content = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)
    unread = UnreadMessagesManager()


    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'read']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"Notification for {self.user.username}: {self.content}"

class MessageHistory(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    edited_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-edited_at']

    def __str__(self):
        return f"History for message {self.message.id} at {self.edited_at}"
