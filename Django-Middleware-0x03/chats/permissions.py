from rest_framework import permissions


class IsSender(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read-only if safe method
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions only if the user owns the object
        return obj.owner == request.user


class IsParticipantOfConversation (permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    """

    def has_permission(self, request, view):
        # Allow access if the user is authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Check if the user is a participant in the conversation
        if request.method in ['PUT', 'PATCH', 'DELETE', 'GET']:
            return request.user in obj.conversation.participants.all()
        return False
