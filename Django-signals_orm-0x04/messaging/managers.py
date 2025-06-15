from django.db import models


class UnreadMessagesManager(models.Manager):
    """
    Custom manager to filter and manage unread messages for users.
    This manager provides methods to work specifically with unread messages.
    """
    
    def get_queryset(self):
        """
        Override the default queryset to return only unread messages.
        Returns messages where read=False.
        """
        return super().get_queryset().filter(read=False)
    
    def unread_for_user(self, user):
        """
        Get all unread messages for a specific user.
        
        Args:
            user: The User object to get unread messages for
            
        Returns:
            QuerySet of unread messages for the specified user
        """
        return self.get_queryset().filter(recipient=user)
    
    def count_unread_for_user(self, user):
        """
        Count the number of unread messages for a specific user.
        
        Args:
            user: The User object to count unread messages for
            
        Returns:
            Integer count of unread messages
        """
        return self.unread_for_user(user).count()
    
    def mark_all_read_for_user(self, user):
        """
        Mark all unread messages as read for a specific user.
        
        Args:
            user: The User object to mark messages as read for
            
        Returns:
            Number of messages that were marked as read
        """
        return self.unread_for_user(user).update(read=True)
    
    def latest_unread_for_user(self, user, limit=5):
        """
        Get the latest unread messages for a user.
        
        Args:
            user: The User object to get messages for
            limit: Maximum number of messages to return (default: 5)
            
        Returns:
            QuerySet of latest unread messages
        """
        return self.unread_for_user(user).order_by('-timestamp')[:limit]