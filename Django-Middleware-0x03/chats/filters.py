from django_filters import rest_framework as filters
from .models import Message


class MessageFilter(filters.FilterSet):
    """FilterSet for filtering messages based on sender, conversation, and sent_at date range.
    This filter allows users to filter messages by the sender's username, the conversation ID,  
    and a range of sent_at timestamps.
    """
    sender = filters.UUIDFilter(field_name='sender', lookup_expr='exact')
    conversation = filters.UUIDFilter(
        field_name='conversation', lookup_expr='exact')
    sent_at = filters.DateTimeFromToRangeFilter(field_name='sent_at')

    class Meta:
        model = Message
        fields = ['sender', 'conversation', 'sent_at']
