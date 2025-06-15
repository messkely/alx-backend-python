from django.test import TestCase
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save, post_delete
from .models import Message, Notification, MessageHistory
from .signals import create_message_notification, log_message_edit, cleanup_user_data

class SignalsTestCase(TestCase):
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
        
        # Delete user1
        self.user1.delete()
        
        # Check if messages were deleted
        self.assertFalse(Message.objects.filter(sender=self.user1).exists())