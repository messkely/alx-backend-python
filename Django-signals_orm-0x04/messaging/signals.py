import logging
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from .models import Message, Notification, MessageHistory

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Signal to create a notification when a new message is created
    """
    if created:
        try:
            with transaction.atomic():
                notification_content = f"You have a new message from {instance.sender.username}"
                Notification.objects.create(
                    user=instance.receiver,
                    message=instance,
                    content=notification_content
                )
                logger.info(f"Notification created for user {instance.receiver.username}")
        except Exception as e:
            logger.error(f"Failed to create notification for message {instance.id}: {e}")

@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Signal to log message edits before saving
    """
    if instance.pk:  # Only for existing messages
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:
                # Log the old content before the edit
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.content
                )
                instance.edited = True
                instance.edited_at = timezone.now()
                instance.edited_by = instance.sender
                logger.info(f"Message {instance.id} edited by {instance.sender.username}")
        except Message.DoesNotExist:
            logger.warning(f"Attempted to edit non-existent message with ID {instance.pk}")
        except Exception as e:
            logger.error(f"Failed to log message edit for message {instance.pk}: {e}")

@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Signal to clean up user-related data when a user is deleted
    """
    try:
        with transaction.atomic():
            # Delete all messages sent and received by the user
            sent_count = Message.objects.filter(sender=instance).count()
            received_count = Message.objects.filter(receiver=instance).count()
            
            Message.objects.filter(sender=instance).delete()
            Message.objects.filter(receiver=instance).delete()
            
            # Delete all notifications for the user
            notification_count = Notification.objects.filter(user=instance).count()
            Notification.objects.filter(user=instance).delete()
            
            logger.info(f"Cleaned up data for user {instance.username}: "
                       f"{sent_count} sent messages, {received_count} received messages, "
                       f"{notification_count} notifications")
    except Exception as e:
        logger.error(f"Failed to cleanup data for user {instance.username}: {e}")

