from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UnreadMessagesManager(models.Manager):
    def unread_for_user(self, user):
        """Return unread messages for a specific user"""
        return self.get_queryset().filter(
            receiver=user, 
            read=False
        ).only('id', 'sender', 'content', 'timestamp')

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    edited = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    parent_message = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='replies'
    )

    objects = models.Manager()  # Default manager
    unread = UnreadMessagesManager()  # Custom manager

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"

    def get_thread_messages(self):
        """Get all messages in this thread using recursive query"""
        return Message.objects.filter(
            models.Q(parent_message=self) | 
            models.Q(id=self.id)
        ).select_related('sender', 'receiver').prefetch_related('replies')

    @classmethod
    def get_conversation_messages(cls, user1, user2):
        """Get all messages between two users with optimized queries"""
        return cls.objects.filter(
            models.Q(sender=user1, receiver=user2) |
            models.Q(sender=user2, receiver=user1)
        ).select_related('sender', 'receiver').prefetch_related(
            'replies__sender', 'replies__receiver'
        ).order_by('timestamp')