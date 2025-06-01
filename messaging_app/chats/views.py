from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Conversation, Message, CustomUser
from .serializers import ConversationSerializer, MessageSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        participant_ids = request.data.get('participant_ids', [])
        if not participant_ids:
            return Response(
                {"detail": "participant_ids is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        participants = CustomUser.objects.filter(user_id__in=participant_ids)
        if participants.count() != len(participant_ids):
            return Response(
                {"detail": "One or more participant_ids are invalid."},
                status=status.HTTP_400_BAD_REQUEST
            )

        conversation = Conversation.objects.create()
        conversation.participants.set(participants)
        conversation.save()

        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        conversation_id = request.data.get('conversation')
        sender_id = request.data.get('sender')
        message_body = request.data.get('message_body')

        if not conversation_id or not sender_id or not message_body:
            return Response(
                {"detail": "conversation, sender, and message_body are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        conversation = get_object_or_404(Conversation, conversation_id=conversation_id)
        sender = get_object_or_404(CustomUser, user_id=sender_id)

        if sender not in conversation.participants.all():
            return Response(
                {"detail": "Sender is not a participant of the conversation."},
                status=status.HTTP_403_FORBIDDEN
            )

        message = Message.objects.create(
            sender=sender,
            conversation=conversation,
            message_body=message_body
        )
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
