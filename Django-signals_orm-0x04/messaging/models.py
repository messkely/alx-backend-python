from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Message(models.Model):
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    recipient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_messages'
    )
    subject = models.CharField(max_length=200)
    body = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)  # Added read boolean field
    
    # Default manager
    objects = models.Manager()
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
    
    def __str__(self):
        return f"{self.subject} - from {self.sender.username} to {self.recipient.username}"
    
    def mark_as_read(self):
        """Mark this message as read"""
        self.read = True
        self.save(update_fields=['read'])
    
    @property
    def is_unread(self):
        """Check if message is unread"""
        return not self.read


# Import custom manager after model definition to avoid circular imports
from .managers import UnreadMessagesManager

# Add custom manager for unread messages
Message.add_to_class('unread', UnreadMessagesManager())