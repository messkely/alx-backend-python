from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UnreadMessagesManager(models.Manager):
    def unread_for_user(self, user):
        """Return unread messages for a specific user with optimized queries"""
        return self.get_queryset().filter(
            receiver=user, 
            read=False
        ).select_related(
            'sender', 'receiver'
        ).prefetch_related(
            'replies__sender', 'replies__receiver'
        ).only('id', 'sender', 'receiver', 'content', 'timestamp', 'read')

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_received_messages')
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
        indexes = [
            models.Index(fields=['sender', 'receiver']),
            models.Index(fields=['receiver', 'read']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"Chat message from {self.sender.username} to {self.receiver.username}"

    def get_thread_messages(self):
        """Get all messages in this thread using optimized recursive query"""
        return Message.objects.filter(
            models.Q(parent_message=self) | 
            models.Q(id=self.id)
        ).select_related(
            'sender', 'receiver', 'parent_message'
        ).prefetch_related(
            models.Prefetch(
                'replies',
                queryset=Message.objects.select_related('sender', 'receiver')
            )
        ).order_by('timestamp')

    @classmethod
    def get_conversation_messages(cls, user1, user2):
        """Get all messages between two users with fully optimized queries"""
        return cls.objects.filter(
            models.Q(sender=user1, receiver=user2) |
            models.Q(sender=user2, receiver=user1)
        ).select_related(
            'sender', 'receiver', 'parent_message'
        ).prefetch_related(
            models.Prefetch(
                'replies',
                queryset=cls.objects.select_related('sender', 'receiver')
            )
        ).order_by('timestamp')

    @classmethod
    def get_user_messages_optimized(cls, user, message_type='all'):
        """
        Get user messages with different filters and optimized queries
        message_type: 'sent', 'received', or 'all'
        """
        base_query = cls.objects.select_related(
            'sender', 'receiver', 'parent_message'
        ).prefetch_related(
            models.Prefetch(
                'replies',
                queryset=cls.objects.select_related('sender', 'receiver')
            )
        )
        
        if message_type == 'sent':
            return base_query.filter(sender=user)
        elif message_type == 'received':
            return base_query.filter(receiver=user)
        else:  # 'all'
            return base_query.filter(
                models.Q(sender=user) | models.Q(receiver=user)
            )