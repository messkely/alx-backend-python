from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from .models import Message, Conversation
from .serializers import MessageSerializer
from .permissions import IsParticipantOfConversation

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        conversation_id = self.request.query_params.get('conversation_id')

        if not conversation_id:
            return Message.objects.none()

        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Message.objects.none()

        if self.request.user not in conversation.participants.all():
            raise APIException(
                detail="You are not a participant of this conversation.",
                code=status.HTTP_403_FORBIDDEN
            )

        return Message.objects.filter(conversation=conversation)

    def perform_create(self, serializer):
        conversation = serializer.validated_data['conversation']

        if self.request.user not in conversation.participants.all():
            raise APIException(
                detail="You are not a participant of this conversation.",
                code=status.HTTP_403_FORBIDDEN
            )

        serializer.save(user=self.request.user)
