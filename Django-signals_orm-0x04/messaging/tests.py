from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save, post_delete
from django.test.utils import override_settings
from .models import Message, Notification, MessageHistory
from .signals import create_message_notification, log_message_edit, cleanup_user_data

class SignalsTestCase(TransactionTestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpass')
        self.user2 = User.objects.create_user(username='user2', password='testpass')

    def test_message_notification_signal(self):
        """Test that a notification is created when a message is sent"""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello, how are you?"
        )
        
        # Check if notification was created
        notification = Notification.objects.filter(user=self.user2, message=message).first()
        self.assertIsNotNone(notification)
        self.assertIn(self.user1.username, notification.content)

    def test_message_edit_signal(self):
        """Test that message history is logged when content is edited"""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original content"
        )
        
        # Edit the message
        message.content = "Edited content"
        message.save()
        
        # Check if history was logged
        history = MessageHistory.objects.filter(message=message).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.old_content, "Original content")
        self.assertTrue(message.edited)

    def test_user_deletion_cleanup(self):
        """Test that user data is cleaned up when user is deleted"""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message"
        )
        
        user1_id = self.user1.id
        
        # Delete user1
        self.user1.delete()
        
        # Check if messages were deleted
        self.assertFalse(Message.objects.filter(sender_id=user1_id).exists())

class MessageModelTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpass')
        self.user2 = User.objects.create_user(username='user2', password='testpass')

    def test_message_creation(self):
        """Test basic message creation"""
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message"
        )
        self.assertEqual(str(message), f"Message from {self.user1.username} to {self.user2.username}")

    def test_message_reply(self):
        """Test message reply functionality"""
        parent_message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original message"
        )
        
        reply_message = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Reply message",
            parent_message=parent_message
        )
        
        self.assertEqual(reply_message.parent_message, parent_message)
        self.assertIn(reply_message, parent_message.replies.all())

