from rest_framework import serializers
from .models import User, Conversation, Message

class MessageSerializer(serializers.ModelSerializer):
    message_body = serializers.CharField()
    sent_at = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['message_id', 'message_body', 'sent_at', 'sender']

    def get_sent_at(self, obj):
        # Format sent_at datetime as ISO 8601 string or any format you prefer
        return obj.sent_at.isoformat()

class ConversationSerializer(serializers.ModelSerializer):
    conversation_id = serializers.CharField(read_only=True)
    participants = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all()
    )
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages']

    def validate_participants(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Conversation must have at least 2 participants.")
        return value

class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(read_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    phone_number = serializers.CharField(allow_blank=True, allow_null=True, required=False)

    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'phone_number']
