import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Override default ID to UUID
    user_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)

    # Already inherited: username, first_name, last_name, email, password, etc.
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    ROLE_CHOICES = (
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    )
    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default='guest')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Conversation(models.Model):
    conversation_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    name = models.CharField(max_length=255)
    participants = models.ManyToManyField('User', related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    message_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    sender = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    conversation = models.ForeignKey(
        'Conversation', on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} to {self.recipient or 'group'}: {self.message_body[:20]}"
