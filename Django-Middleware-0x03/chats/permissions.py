from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Allows only participants of a conversation to send, view, update, or delete messages.
    """

    def has_permission(self, request, view):
        # Only allow authenticated users to proceed
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Get the conversation object (if obj is a message, get obj.conversation)
        conversation = getattr(obj, 'conversation', obj)

        # Check if user is part of the conversation participants
        is_participant = request.user in conversation.participants.all()

        # Allow only participants to read, send, update, or delete messages
        if request.method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
            return is_participant

        # Deny all other methods
        return False
