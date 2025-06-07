from rest_framework import permissions
from .models import Conversation

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to allow only participants of a conversation
    to access related messages or the conversation itself.
    """

    def has_object_permission(self, request, view, obj):
        # If the object is a Message, get its conversation
        conversation = getattr(obj, 'conversation', obj)
        return request.user in conversation.participants.all()

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
